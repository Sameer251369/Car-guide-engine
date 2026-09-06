# Production deployment

If Render's Root Directory is `backend`, use this start command:

```bash
bash start.sh
```

If Render's Root Directory is blank (the repository root), use:

```bash
bash backend/start.sh
```

## Cloudinary media storage

Set these environment variables in Render and in `backend/.env` for local
development. Uploaded vehicle images from Django Admin and the frontend admin
are stored in Cloudinary and remain available across deploys:

```text
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

Do not commit `backend/.env` or expose the API secret in frontend code.

The startup script applies migrations and repairs the calculator dataset before
starting Gunicorn. This is safe to run on every deploy because the repair
command is idempotent.

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
