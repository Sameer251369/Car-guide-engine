import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carguide.settings')
django.setup()

import json
from decimal import Decimal
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal): return str(obj)
        return super(DecimalEncoder, self).default(obj)
from calculator.services import calculate_on_road_price
from portfolio.models import Vehicle
from calculator.models import State

v_gurkha = Vehicle.objects.filter(name__icontains='gurkha').first()
v_creta = Vehicle.objects.filter(name__icontains='creta electric').first()
dl = State.objects.filter(code='DL').first()

if v_gurkha and dl:
    res = calculate_on_road_price(v_gurkha, dl)
    print("Gurkha:", json.dumps(res, cls=DecimalEncoder, indent=2))
if v_creta and dl:
    res = calculate_on_road_price(v_creta, dl)
    print("Creta EV:", json.dumps(res, cls=DecimalEncoder, indent=2))
