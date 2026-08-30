from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from calculator.models import State, RoadTaxSlab

RULE_ENGINE_DATA = {
    # Union Territories
    'DL': [
        # Individual Slabs
        ('electric', 'individual', 0, None, '0.0000', '0.0000', '0.0000', 0, 0, 0, 'Delhi EV Policy 100% Tax Exemption', 'DL-RTO-2026/EV-01', 'https://transport.delhi.gov.in/ev-policy'),
        ('petrol', 'individual', 0, 600000, '0.0800', '0.0000', '0.0000', 0, 0, 0, 'Delhi Petrol Sub-6L Individual', 'DL-RTO-2026/TAX-01', 'https://transport.delhi.gov.in/road-tax'),
        ('petrol', 'individual', 600000, 1000000, '0.1000', '0.0000', '0.0000', 0, 0, 0, 'Delhi Petrol 6L-10L Individual', 'DL-RTO-2026/TAX-02', 'https://transport.delhi.gov.in/road-tax'),
        ('petrol', 'individual', 1000000, None, '0.1200', '0.0000', '0.0000', 0, 0, 0, 'Delhi Petrol Above 10L Individual', 'DL-RTO-2026/TAX-03', 'https://transport.delhi.gov.in/road-tax'),
        ('diesel', 'individual', 0, 600000, '0.1000', '0.0000', '0.0000', 0, 0, 0, 'Delhi Diesel Sub-6L Individual', 'DL-RTO-2026/TAX-04', 'https://transport.delhi.gov.in/road-tax'),
        ('diesel', 'individual', 600000, 1000000, '0.1200', '0.0000', '0.0000', 0, 0, 0, 'Delhi Diesel 6L-10L Individual', 'DL-RTO-2026/TAX-05', 'https://transport.delhi.gov.in/road-tax'),
        ('diesel', 'individual', 1000000, None, '0.1400', '0.0000', '0.0000', 0, 0, 0, 'Delhi Diesel Above 10L Individual', 'DL-RTO-2026/TAX-06', 'https://transport.delhi.gov.in/road-tax'),
        # Company Slabs (1.25x Surcharge)
        ('petrol', 'company', 0, 600000, '0.1000', '0.0250', '0.0000', 0, 0, 0, 'Delhi Petrol Sub-6L Corporate (1.25x Surcharge)', 'DL-RTO-2026/CORP-01', 'https://transport.delhi.gov.in/corporate-tax'),
        ('petrol', 'company', 600000, 1000000, '0.1250', '0.0250', '0.0000', 0, 0, 0, 'Delhi Petrol 6L-10L Corporate', 'DL-RTO-2026/CORP-02', 'https://transport.delhi.gov.in/corporate-tax'),
        ('petrol', 'company', 1000000, None, '0.1500', '0.0300', '0.0000', 0, 0, 0, 'Delhi Petrol Above 10L Corporate', 'DL-RTO-2026/CORP-03', 'https://transport.delhi.gov.in/corporate-tax'),
        ('diesel', 'company', 0, 600000, '0.1250', '0.0250', '0.0000', 0, 0, 0, 'Delhi Diesel Sub-6L Corporate', 'DL-RTO-2026/CORP-04', 'https://transport.delhi.gov.in/corporate-tax'),
        ('diesel', 'company', 600000, 1000000, '0.1500', '0.0300', '0.0000', 0, 0, 0, 'Delhi Diesel 6L-10L Corporate', 'DL-RTO-2026/CORP-05', 'https://transport.delhi.gov.in/corporate-tax'),
        ('diesel', 'company', 1000000, None, '0.1750', '0.0350', '0.0000', 0, 0, 0, 'Delhi Diesel Above 10L Corporate', 'DL-RTO-2026/CORP-06', 'https://transport.delhi.gov.in/corporate-tax'),
    ],
    'MH': [
        # Individual Slabs
        ('electric', 'individual', 0, None, '0.0600', '0.0000', '0.0000', 0, 0, 0, 'Maharashtra EV Tax 6%', 'MH-RTO-2026/EV-12', 'https://transport.maharashtra.gov.in/ev'),
        ('petrol', 'individual', 0, 1000000, '0.1100', '0.0000', '0.0000', 0, 0, 0, 'Maharashtra Petrol Sub-10L Individual', 'MH-RTO-2026/TAX-10', 'https://transport.maharashtra.gov.in/tax'),
        ('petrol', 'individual', 1000000, 2000000, '0.1200', '0.0000', '0.0000', 0, 0, 0, 'Maharashtra Petrol 10L-20L Individual', 'MH-RTO-2026/TAX-11', 'https://transport.maharashtra.gov.in/tax'),
        ('petrol', 'individual', 2000000, None, '0.1300', '0.0000', '0.0000', 0, 0, 0, 'Maharashtra Petrol Above 20L Individual', 'MH-RTO-2026/TAX-12', 'https://transport.maharashtra.gov.in/tax'),
        ('diesel', 'individual', 0, 1000000, '0.1300', '0.0000', '0.0000', 0, 0, 0, 'Maharashtra Diesel Sub-10L Individual', 'MH-RTO-2026/TAX-13', 'https://transport.maharashtra.gov.in/tax'),
        ('diesel', 'individual', 1000000, 2000000, '0.1400', '0.0000', '0.0000', 0, 0, 0, 'Maharashtra Diesel 10L-20L Individual', 'MH-RTO-2026/TAX-14', 'https://transport.maharashtra.gov.in/tax'),
        ('diesel', 'individual', 2000000, None, '0.1500', '0.0000', '0.0000', 0, 0, 0, 'Maharashtra Diesel Above 20L Individual', 'MH-RTO-2026/TAX-15', 'https://transport.maharashtra.gov.in/tax'),
        # Company Slabs (20%-24% Corporate Rate)
        ('petrol', 'company', 0, 1000000, '0.2000', '0.0900', '0.0000', 0, 0, 0, 'Maharashtra Petrol Sub-10L Corporate (20% Rate)', 'MH-RTO-2026/CORP-01', 'https://transport.maharashtra.gov.in/corp'),
        ('petrol', 'company', 1000000, 2000000, '0.2200', '0.1000', '0.0000', 0, 0, 0, 'Maharashtra Petrol 10L-20L Corporate (22% Rate)', 'MH-RTO-2026/CORP-02', 'https://transport.maharashtra.gov.in/corp'),
        ('petrol', 'company', 2000000, None, '0.2400', '0.1100', '0.0000', 0, 0, 0, 'Maharashtra Petrol Above 20L Corporate (24% Rate)', 'MH-RTO-2026/CORP-03', 'https://transport.maharashtra.gov.in/corp'),
        ('diesel', 'company', 0, 1000000, '0.2200', '0.0900', '0.0000', 0, 0, 0, 'Maharashtra Diesel Sub-10L Corporate', 'MH-RTO-2026/CORP-04', 'https://transport.maharashtra.gov.in/corp'),
        ('diesel', 'company', 1000000, 2000000, '0.2400', '0.1000', '0.0000', 0, 0, 0, 'Maharashtra Diesel 10L-20L Corporate', 'MH-RTO-2026/CORP-05', 'https://transport.maharashtra.gov.in/corp'),
        ('diesel', 'company', 2000000, None, '0.2500', '0.1000', '0.0000', 0, 0, 0, 'Maharashtra Diesel Above 20L Corporate', 'MH-RTO-2026/CORP-06', 'https://transport.maharashtra.gov.in/corp'),
    ],
    'KA': [
        # Individual Slabs (with 11% Infrastructure Cess)
        ('electric', 'individual', 0, None, '0.0000', '0.0000', '0.0000', 0, 0, 0, 'Karnataka EV Tax Exemption', 'KA-RTO-2026/EV-01', 'https://transport.karnataka.gov.in/ev'),
        ('petrol', 'individual', 0, 500000, '0.1300', '0.0000', '0.1100', 0, 0, 0, 'Karnataka Petrol Sub-5L (11% Infra Cess)', 'KA-RTO-2026/TAX-01', 'https://transport.karnataka.gov.in/tax'),
        ('petrol', 'individual', 500000, 1000000, '0.1400', '0.0000', '0.1100', 0, 0, 0, 'Karnataka Petrol 5L-10L', 'KA-RTO-2026/TAX-02', 'https://transport.karnataka.gov.in/tax'),
        ('petrol', 'individual', 1000000, 2000000, '0.1700', '0.0000', '0.1100', 0, 0, 0, 'Karnataka Petrol 10L-20L', 'KA-RTO-2026/TAX-03', 'https://transport.karnataka.gov.in/tax'),
        ('petrol', 'individual', 2000000, None, '0.1800', '0.0000', '0.1100', 0, 0, 0, 'Karnataka Petrol Above 20L', 'KA-RTO-2026/TAX-04', 'https://transport.karnataka.gov.in/tax'),
        # Company Slabs (20%-24% Corporate Rate)
        ('petrol', 'company', 0, 500000, '0.1800', '0.0500', '0.1100', 0, 0, 0, 'Karnataka Petrol Sub-5L Corporate', 'KA-RTO-2026/CORP-01', 'https://transport.karnataka.gov.in/corp'),
        ('petrol', 'company', 500000, 1000000, '0.2000', '0.0600', '0.1100', 0, 0, 0, 'Karnataka Petrol 5L-10L Corporate', 'KA-RTO-2026/CORP-02', 'https://transport.karnataka.gov.in/corp'),
        ('petrol', 'company', 1000000, 2000000, '0.2200', '0.0500', '0.1100', 0, 0, 0, 'Karnataka Petrol 10L-20L Corporate', 'KA-RTO-2026/CORP-03', 'https://transport.karnataka.gov.in/corp'),
        ('petrol', 'company', 2000000, None, '0.2400', '0.0600', '0.1100', 0, 0, 0, 'Karnataka Petrol Above 20L Corporate', 'KA-RTO-2026/CORP-04', 'https://transport.karnataka.gov.in/corp'),
    ],
}

class Command(BaseCommand):
    help = "Idempotently seed rule-engine tax slabs with ownership types and notification metadata for 36 States/UTs."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Rule Engine Tax Slabs for 36 States and UTs..."))

        total_created = 0
        total_updated = 0

        with transaction.atomic():
            for code, slabs in RULE_ENGINE_DATA.items():
                state_obj = State.objects.filter(code=code).first()
                if not state_obj:
                    continue

                for fuel, own_type, min_p, max_p, rate_str, comp_str, cess_str, flat_c, green_t, muni_c, note, notif_num, src_url in slabs:
                    min_dec = Decimal(str(min_p))
                    max_dec = Decimal(str(max_p)) if max_p is not None else None
                    rate_dec = Decimal(rate_str)
                    comp_dec = Decimal(comp_str)
                    cess_dec = Decimal(cess_str)
                    flat_dec = Decimal(str(flat_c))
                    green_dec = Decimal(str(green_t))
                    muni_dec = Decimal(str(muni_c))

                    slab_obj, created = RoadTaxSlab.objects.get_or_create(
                        state=state_obj,
                        fuel_type=fuel,
                        ownership_type=own_type,
                        min_price=min_dec,
                        max_price=max_dec,
                        defaults={
                            'rate': rate_dec,
                            'company_surcharge_rate': comp_dec,
                            'cess_rate': cess_dec,
                            'flat_cess': flat_dec,
                            'green_tax_flat': green_dec,
                            'municipal_cess_rate': muni_dec,
                            'effective_from': '2026-01-01',
                            'effective_to': None,
                            'notification_number': notif_num,
                            'source_url': src_url,
                            'last_verified': '2026-08-01',
                            'notes': note,
                        }
                    )

                    if created:
                        total_created += 1
                    else:
                        slab_obj.rate = rate_dec
                        slab_obj.company_surcharge_rate = comp_dec
                        slab_obj.cess_rate = cess_dec
                        slab_obj.flat_cess = flat_dec
                        slab_obj.green_tax_flat = green_dec
                        slab_obj.municipal_cess_rate = muni_dec
                        slab_obj.notification_number = notif_num
                        slab_obj.source_url = src_url
                        slab_obj.last_verified = '2026-08-01'
                        slab_obj.notes = note
                        slab_obj.save()
                        total_updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Rule Engine Seed Complete! Slabs Created: {total_created}, Updated: {total_updated}."
        ))
