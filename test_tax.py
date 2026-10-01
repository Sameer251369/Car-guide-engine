from calculator.services import calculate_on_road_price
from portfolio.models import Vehicle
from calculator.models import State

vehicles = Vehicle.objects.filter(name__icontains='gurkha') | Vehicle.objects.filter(name__icontains='creta electric')
states = State.objects.filter(is_active=True)[:3] # just test on a few states

for v in vehicles:
    for s in states:
        res = calculate_on_road_price(v, s)
        tax = 0
        if res.get('price_breakdown'):
            tax = res['price_breakdown'].get('2. State Lifetime Road Tax', 0)
        print(f"Vehicle: {v.name}, State: {s.name}, Tax: {tax}")
