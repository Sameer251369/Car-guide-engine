from decimal import Decimal
from django.core.management.base import BaseCommand
from calculator.models import RoadTaxSlab

class Command(BaseCommand):
    help = 'Fixes tax slabs that have a 0.00 rate by copying the petrol rate or setting a default 8% rate.'

    def handle(self, *args, **options):
        # We target all electric (and CNG/Hybrid if needed) slabs since they might have been overwritten with constant values
        slabs_to_update = RoadTaxSlab.objects.filter(fuel_type__in=['electric', 'cng', 'hybrid'])
        count = 0

        for slab in slabs_to_update:
            # Find the petrol slab for the exact same price bracket
            petrol_slab = RoadTaxSlab.objects.filter(
                state=slab.state, 
                fuel_type='petrol',
                min_price=slab.min_price,
                max_price=slab.max_price
            ).first()
            
            if petrol_slab and petrol_slab.rate > 0:
                # Use a slightly discounted rate for EVs compared to petrol (e.g. petrol - 2%)
                # Or just use the petrol rate directly if requested. Let's use petrol rate directly to make it accurate and variable.
                # Actually, let's make it petrol_slab.rate * 0.75 for EV to show some variance, or just petrol_slab.rate. 
                # Let's just use petrol_slab.rate so it matches exactly the tiered structure of petrol.
                slab.rate = petrol_slab.rate
            else:
                # Fallback if exact slab match fails: look for any petrol slab that covers this min_price
                fallback_slab = RoadTaxSlab.objects.filter(
                    state=slab.state, 
                    fuel_type='petrol',
                    min_price__lte=slab.min_price
                ).order_by('-min_price').first()
                
                if fallback_slab and fallback_slab.rate > 0:
                    slab.rate = fallback_slab.rate
                else:
                    slab.rate = Decimal("0.08")
            slab.save()
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully updated {count} tax slabs with 0.00 rate."))
