from django.db import models
from django.utils.text import slugify

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    logo_url = models.URLField(max_length=500, blank=True, help_text="Image URL or Cloudinary URL")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.name)


class Vehicle(models.Model):
    BODY_TYPE_CHOICES = [
        ('Convertible', 'Convertible'),
        ('Coupe', 'Coupe'),
        ('Coupe SUV', 'Coupe SUV'),
        ('Crossover', 'Crossover'),
        ('Fastback', 'Fastback'),
        ('Hatchback', 'Hatchback'),
        ('Liftback', 'Liftback'),
        ('Luxury SUV', 'Luxury SUV'),
        ('Luxury Sedan', 'Luxury Sedan'),
        ('MPV', 'MPV'),
        ('Performance SUV', 'Performance SUV'),
        ('Pickup', 'Pickup'),
        ('SUV', 'SUV'),
        ('Sedan', 'Sedan'),
        ('Sports Car', 'Sports Car'),
        ('Sports Sedan', 'Sports Sedan'),
        ('Van', 'Van'),
    ]

    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='vehicles')
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    body_type = models.CharField(max_length=50, default='SUV')
    fuel_type = models.CharField(max_length=50, default='Petrol')
    ev_hybrid_cng_flag = models.CharField(max_length=50, default='No', help_text="No, EV, Hybrid, CNG, Hybrid/CNG, Hybrid/Petrol")
    starting_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Starting ex-showroom price in INR")
    top_variant_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Top variant ex-showroom price in INR")
    ex_showroom_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Ex-showroom price (alias/starting price)")
    seats = models.IntegerField(null=True, blank=True, help_text="Seating capacity")
    transmission = models.CharField(max_length=100, blank=True, default='Manual/Automatic')
    needs_review = models.BooleanField(default=False, help_text="True for TBA prices or corrupt seat values")
    data_source = models.CharField(max_length=50, default='master_db_import', help_text="master_db_import | manual")
    key_specs = models.JSONField(default=dict, blank=True, help_text="e.g. {'engine': '1.5L Turbo', 'mileage': '18.2 kmpl'}")
    description = models.TextField(blank=True, default="", help_text="Detailed vehicle overview and description")
    is_featured = models.BooleanField(default=False)
    is_tba = models.BooleanField(default=False, help_text="True if car prices are to be announced")
    is_active = models.BooleanField(default=True)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-is_featured', 'brand__name', 'name']
        unique_together = ('brand', 'name')

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.brand.name}-{self.name}")
        else:
            base_slug = self.slug

        slug = base_slug
        counter = 1
        while Vehicle.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        self.slug = slug

        if self.starting_price and (not self.ex_showroom_price or self.ex_showroom_price == 0):
            self.ex_showroom_price = self.starting_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand.name} {self.name}"


class VehicleVariant(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='variants')
    variant_name = models.CharField(max_length=100)
    ex_showroom_price = models.DecimalField(max_digits=12, decimal_places=2)
    fuel_type = models.CharField(max_length=50, blank=True)
    transmission = models.CharField(max_length=50, default='Manual')

    objects = models.Manager()

    class Meta:
        ordering = ['ex_showroom_price']

    def __str__(self):
        price_val = int(self.ex_showroom_price) if self.ex_showroom_price else 0
        return f"{self.vehicle.name} - {self.variant_name} (₹{price_val:,.0f})"


class VehicleImage(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='images')
    image_url = models.ImageField(upload_to='vehicle_images/', blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)

    objects = models.Manager()

    class Meta:
        ordering = ['-is_primary', 'display_order']

    def __str__(self):
        return f"Image for {self.vehicle.name}"
