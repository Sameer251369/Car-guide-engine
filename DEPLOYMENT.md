# Production deployment

Run these commands from the `backend` directory after installing `requirements.txt`:

```bash
python manage.py migrate
python seed_data_comprehensive.py
python manage.py seed_calculator_data
```

`seed_calculator_data` is idempotent. It repairs road-tax slabs for all active states that exist in the database and ensures the default insurance estimate and included dealer charge are present. Run it after any vehicle/state import and on every deploy that uses a new database.

Verify the repair before switching traffic:

```bash
python manage.py shell -c "from calculator.models import State, RoadTaxSlab, InsuranceEstimate, DealerCharge; print(State.objects.filter(is_active=True).count(), RoadTaxSlab.objects.count(), InsuranceEstimate.objects.count(), DealerCharge.objects.filter(is_default_included=True).count())"
```

The expected production baseline is 36 active states, at least one tax slab per active state, one fallback insurance estimate, and at least one included dealer charge.
