from decimal import Decimal
from django.core.management.base import BaseCommand
from calculator.models import RoadTaxSlab

class Command(BaseCommand):
    help = 'Fixes tax slabs that have a 0.00 rate by copying the petrol rate or setting a default 8% rate.'

    def handle(self, *args, **options):
        # Target electric (and CNG/Hybrid if needed) slabs
        slabs_to_update = list(RoadTaxSlab.objects.filter(fuel_type__in=['electric', 'cng', 'hybrid']))
        
        # Pre-fetch all petrol slabs for the states involved
        petrol_slabs = list(RoadTaxSlab.objects.filter(fuel_type='petrol'))
        
        count = 0
        slabs_to_save = []

        for slab in slabs_to_update:
            # Find exact petrol slab match
            exact_match = next((p for p in petrol_slabs if p.state_id == slab.state_id and p.min_price == slab.min_price and p.max_price == slab.max_price), None)
            
            if exact_match and exact_match.rate > 0:
                slab.rate = exact_match.rate
            else:
                # Find fallback
                fallbacks = [p for p in petrol_slabs if p.state_id == slab.state_id and p.min_price <= slab.min_price]
                if fallbacks:
                    best_fallback = max(fallbacks, key=lambda p: p.min_price)
                    if best_fallback.rate > 0:
                        slab.rate = best_fallback.rate
                    else:
                        slab.rate = Decimal("0.08")
                else:
                    slab.rate = Decimal("0.08")
            
            slabs_to_save.append(slab)
            count += 1

        RoadTaxSlab.objects.bulk_update(slabs_to_save, ['rate'])

        self.stdout.write(self.style.SUCCESS(f"Successfully updated {count} tax slabs in bulk."))
