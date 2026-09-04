from decimal import Decimal

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from calculator.models import DealerCharge, InsuranceEstimate, RoadTaxSlab, State


class Command(BaseCommand):
    help = "Repair the production calculator dataset: state tax slabs, insurance, and dealer charges."

    def handle(self, *args, **options):
        with transaction.atomic():
            call_command("seed_tax_slabs_36", verbosity=0)
            InsuranceEstimate.objects.get_or_create(
                state=None,
                defaults={"rate_percent": Decimal("3.50")},
            )
            DealerCharge.objects.get_or_create(
                name="Standard Dealer Logistics & Handling",
                defaults={
                    "amount": Decimal("1500.00"),
                    "is_default_included": True,
                },
            )

        missing_states = list(
            State.objects.filter(is_active=True)
            .exclude(tax_slabs__isnull=False)
            .values_list("code", flat=True)
        )
        if missing_states:
            raise CommandError(
                "Active states without calculator tax slabs: "
                + ", ".join(missing_states)
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Calculator data is ready: "
                f"{RoadTaxSlab.objects.count()} tax slabs, "
                f"{InsuranceEstimate.objects.count()} insurance defaults, "
                f"{DealerCharge.objects.filter(is_default_included=True).count()} included dealer charges."
            )
        )
