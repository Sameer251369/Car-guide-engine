from django.db import models
from portfolio.models import Vehicle

class State(models.Model):
    PRICE_BASIS_CHOICES = [
        ('ex_showroom', 'Ex-Showroom Price'),
        ('pre_gst', 'Pre-GST Price (Gujarat, Chandigarh, Jharkhand basis)'),
    ]

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, help_text="e.g. DL, MH, KA, GJ, CH")
    price_basis = models.CharField(max_length=20, choices=PRICE_BASIS_CHOICES, default='ex_showroom')
    pre_gst_factor = models.DecimalField(max_digits=5, decimal_places=4, default=0.7200, help_text="Pre-GST price factor if applicable (e.g. 0.72 = 72% of ex-showroom)")
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=600.00)
    smart_card_fee = models.DecimalField(max_digits=10, decimal_places=2, default=200.00)
    hsrp_fee = models.DecimalField(max_digits=10, decimal_places=2, default=400.00)
    hypothecation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=1500.00, help_text="Charged if vehicle is financed")
    fastag_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    misc_fee = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00, help_text="Fixed misc charges baked into spreadsheet OTR")
    data_source_note = models.TextField(blank=True, default="Estimated 2026 road-tax basis; see PDF methodology.", help_text="Surface in UI calculator disclaimer")
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class VehicleStateEstimate(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='state_estimates')
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='vehicle_estimates')
    start_otr = models.DecimalField(max_digits=12, decimal_places=2, help_text="Precomputed starting variant OTR price")
    top_otr = models.DecimalField(max_digits=12, decimal_places=2, help_text="Precomputed top variant OTR price")
    imported_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ['vehicle', 'state']
        unique_together = ('vehicle', 'state')

    def __str__(self):
        start_val = int(self.start_otr) if self.start_otr else 0
        top_val = int(self.top_otr) if self.top_otr else 0
        return f"{self.vehicle.brand.name} {self.vehicle.name} in {self.state.name} (₹{start_val:,.0f} - ₹{top_val:,.0f})"


class StateOnRoadPrice(models.Model):
    car = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="state_prices")
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="car_prices")
    start_ex_showroom = models.BigIntegerField(null=True, blank=True)   # paise-free INR, null = TBA
    top_ex_showroom = models.BigIntegerField(null=True, blank=True)
    start_on_road = models.BigIntegerField(null=True, blank=True)
    top_on_road = models.BigIntegerField(null=True, blank=True)

    objects = models.Manager()

    class Meta:
        unique_together = ("car", "state")

    def __str__(self):
        return f"{self.car.brand.name} {self.car.name} in {self.state.name} (Ex: {self.start_ex_showroom} | OTR: {self.start_on_road})"


class RoadTaxSlab(models.Model):
    FUEL_CHOICES = [
        ('all', 'All Fuel Types'),
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('cng', 'CNG'),
        ('electric', 'Electric / EV'),
        ('hybrid', 'Hybrid'),
    ]

    OWNERSHIP_CHOICES = [
        ('all', 'All Ownership Types'),
        ('individual', 'Individual Ownership'),
        ('company', 'Company / Corporate Ownership'),
    ]

    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='tax_slabs')
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default='all')
    ownership_type = models.CharField(max_length=20, choices=OWNERSHIP_CHOICES, default='all')
    min_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    max_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Leave blank for no upper bound")
    rate = models.DecimalField(max_digits=5, decimal_places=4, help_text="Rate as decimal e.g. 0.13 = 13%, 0.00 = 0% EV rate")
    company_surcharge_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.0000, help_text="Additional tax rate for company registration e.g. 0.04 = +4%")
    cess_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.0000, help_text="Additional road safety/transport cess rate as decimal e.g. 0.01 = 1%")
    flat_cess = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Flat cess amount in INR e.g. 500.00")
    green_tax_flat = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Green tax / environmental levy in INR")
    municipal_cess_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.0000, help_text="City municipal / infrastructure cess rate")
    temp_registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Temporary inter-state RTO registration fee")
    effective_from = models.DateField(default='2026-01-01', help_text="Rule effective start date")
    effective_to = models.DateField(null=True, blank=True, help_text="Rule effective expiry date")
    notification_number = models.CharField(max_length=150, default='GSR-2026/RTO-STD', help_text="Official RTO gazette notification ID")
    source_url = models.URLField(max_length=500, default='https://morth.nic.in', help_text="Official RTO notification portal URL")
    last_verified = models.DateField(default='2026-08-01', help_text="Last verification date against RTO gazette")
    notes = models.TextField(blank=True, default="", help_text="Slab-specific RTO notification notes")

    objects = models.Manager()

    class Meta:
        ordering = ['state', 'min_price']

    def __str__(self):
        max_str = f"₹{int(self.max_price):,.0f}" if self.max_price else "Above"
        min_str = f"₹{int(self.min_price):,.0f}" if self.min_price else "₹0"
        rate_str = float(self.rate * 100) if self.rate else 0.0
        return f"{self.state.code} | {self.fuel_type} ({self.ownership_type}) | {min_str} - {max_str} : {rate_str}%"




class InsuranceEstimate(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True, blank=True, related_name='insurance_estimates', help_text="Leave blank for national fallback default")
    rate_percent = models.DecimalField(max_digits=5, decimal_places=2, default=3.50, help_text="Percentage of ex-showroom price (e.g. 3.50 = 3.5%)")

    objects = models.Manager()

    def __str__(self):
        state_str = self.state.name if self.state else "Global Fallback"
        return f"Insurance Estimate ({state_str}): {self.rate_percent}%"


class DealerCharge(models.Model):
    name = models.CharField(max_length=150, default="Dealer Handling & Logistics")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=1500.00)
    is_default_included = models.BooleanField(default=True)

    objects = models.Manager()

    def __str__(self):
        amt_str = int(self.amount) if self.amount else 0
        return f"{self.name}: ₹{amt_str:,.0f}"
