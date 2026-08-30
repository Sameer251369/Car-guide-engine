from django.contrib import admin
from .models import Brand, Vehicle, VehicleVariant, VehicleImage

class VehicleVariantInline(admin.TabularInline):
    model = VehicleVariant
    extra = 1

class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'body_type', 'fuel_type', 'ex_showroom_price', 'is_featured', 'is_active')
    list_filter = ('brand', 'body_type', 'fuel_type', 'is_featured', 'is_active')
    search_fields = ('name', 'brand__name')
    prepopulated_fields = {'slug': ('brand', 'name')}
    inlines = [VehicleVariantInline, VehicleImageInline]

@admin.register(VehicleVariant)
class VehicleVariantAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'variant_name', 'ex_showroom_price', 'transmission', 'fuel_type')
    list_filter = ('vehicle__brand', 'transmission')
    search_fields = ('vehicle__name', 'variant_name')
