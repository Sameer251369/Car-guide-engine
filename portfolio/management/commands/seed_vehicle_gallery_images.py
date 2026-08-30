from urllib.parse import quote

from django.core.management.base import BaseCommand

from portfolio.models import Vehicle, VehicleImage

LABELS = ['front', 'profile', 'detail', 'interior']


def make_svg(label, title, accent, subtitle):
    svg = f"""
    <svg xmlns='http://www.w3.org/2000/svg' width='1200' height='800' viewBox='0 0 1200 800'>
      <defs>
        <linearGradient id='bg' x1='0' x2='1'>
          <stop offset='0%' stop-color='{accent}' />
          <stop offset='100%' stop-color='#0f172a' />
        </linearGradient>
      </defs>
      <rect width='1200' height='800' fill='url(#bg)'/>
      <g opacity='0.18'>
        <circle cx='120' cy='130' r='120' fill='#ffffff'/>
        <circle cx='1020' cy='680' r='160' fill='#ffffff'/>
      </g>
      <rect x='110' y='110' width='980' height='580' rx='28' fill='rgba(15,23,42,0.52)' stroke='rgba(255,255,255,0.22)'/>
      <text x='600' y='315' text-anchor='middle' font-size='44' font-family='Arial, sans-serif' font-weight='700' fill='#f8fafc' letter-spacing='2'>{title}</text>
      <text x='600' y='390' text-anchor='middle' font-size='76' font-family='Arial, sans-serif' font-weight='800' fill='#f8fafc'>{label}</text>
      <text x='600' y='470' text-anchor='middle' font-size='24' font-family='Arial, sans-serif' fill='#e2e8f0' letter-spacing='3'>{subtitle}</text>
    </svg>
    """
    return 'data:image/svg+xml;charset=utf-8,' + quote(svg)


class Command(BaseCommand):
    help = 'Populate each vehicle with model-specific SVG gallery placeholders instead of random car photos.'

    def handle(self, *args, **options):
        vehicles = Vehicle.objects.filter(is_active=True).select_related('brand')
        created = 0

        for vehicle in vehicles:
            vehicle.images.all().delete()
            model_name = f"{vehicle.brand.name} {vehicle.name}"
            accent = '#f59e0b' if vehicle.fuel_type.lower() in {'petrol', 'diesel'} else '#10b981'
            label_prefix = vehicle.body_type or 'SUV'

            for idx, label in enumerate(LABELS):
                image_url = make_svg(
                    label.upper(),
                    model_name,
                    accent,
                    f'{label_prefix} • {vehicle.fuel_type or "Fuel"}'
                )
                VehicleImage.objects.create(
                    vehicle=vehicle,
                    image_url=image_url,
                    alt_text=f"{model_name} {label} view",
                    is_primary=(idx == 0),
                    display_order=idx,
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created} model-specific gallery images for {vehicles.count()} vehicles.'))
