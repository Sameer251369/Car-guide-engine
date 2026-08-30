from django.core.management.base import BaseCommand
import csv
from pathlib import Path
from portfolio.models import Vehicle


class Command(BaseCommand):
    help = 'Export vehicles with needs_review=True to a CSV for manual review'

    def add_arguments(self, parser):
        parser.add_argument('--output', type=str, default='flagged_vehicles_review.csv', help='Output CSV path (relative to repo root)')

    def handle(self, *args, **options):
        out_path = Path(options['output'])
        vehicles = Vehicle.objects.filter(needs_review=True).select_related('brand')

        if not vehicles.exists():
            self.stdout.write(self.style.NOTICE('No flagged vehicles found.'))
            return

        with out_path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'id', 'brand', 'name', 'slug', 'starting_price', 'top_variant_price',
                'seats', 'transmission', 'is_active', 'data_source', 'created_at', 'flag_reason'
            ])

            for v in vehicles.order_by('brand__name', 'name'):
                reasons = []
                if not v.starting_price or v.starting_price == 0:
                    reasons.append('TBA/Missing starting_price')
                if not v.top_variant_price or v.top_variant_price == 0:
                    reasons.append('TBA/Missing top_variant_price')
                if v.seats is None:
                    reasons.append('Invalid/Corrupt seats')

                writer.writerow([
                    v.id,
                    v.brand.name if v.brand else '',
                    v.name,
                    v.slug,
                    str(v.starting_price) if v.starting_price is not None else '',
                    str(v.top_variant_price) if v.top_variant_price is not None else '',
                    v.seats if v.seats is not None else '',
                    v.transmission or '',
                    'Yes' if v.is_active else 'No',
                    v.data_source or '',
                    v.created_at.isoformat() if v.created_at else '',
                    '; '.join(reasons),
                ])

        self.stdout.write(self.style.SUCCESS(f'Exported {vehicles.count()} flagged vehicles to {out_path.resolve()}'))
