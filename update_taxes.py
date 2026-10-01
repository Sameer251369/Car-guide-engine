from decimal import Decimal
from calculator.models import RoadTaxSlab

# Find all slabs with 0.00 rate
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

print(f"Updated {count} tax slabs with 0.00 rate.")
