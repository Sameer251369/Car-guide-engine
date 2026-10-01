from decimal import Decimal
from django.core.management.base import BaseCommand
from calculator.models import RoadTaxSlab

class Command(BaseCommand):
    help = 'Fixes tax slabs that have a 0.00 rate by copying the petrol rate or setting a default 8% rate.'

    def handle(self, *args, **options):
        slabs_to_update = RoadTaxSlab.objects.filter(rate=Decimal("0.00"))
        count = 0

        for slab in slabs_to_update:
            # Try to find a petrol slab for the same state
            petrol_slab = RoadTaxSlab.objects.filter(state=slab.state, fuel_type='petrol').first()
            if petrol_slab:
                slab.rate = petrol_slab.rate
            else:
                # Default fallback
                slab.rate = Decimal("0.08")
            slab.save()
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully updated {count} tax slabs with 0.00 rate."))
