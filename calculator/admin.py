from django.contrib import admin
from .models import State, RoadTaxSlab, InsuranceEstimate, DealerCharge

class RoadTaxSlabInline(admin.TabularInline):
    model = RoadTaxSlab
    extra = 1

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'price_basis', 'registration_fee', 'fastag_fee', 'is_active')
    list_filter = ('price_basis', 'is_active')
    search_fields = ('name', 'code')
    inlines = [RoadTaxSlabInline]

@admin.register(RoadTaxSlab)
class RoadTaxSlabAdmin(admin.ModelAdmin):
    list_display = ('state', 'fuel_type', 'min_price', 'max_price', 'rate')
    list_filter = ('state', 'fuel_type')

@admin.register(InsuranceEstimate)
class InsuranceEstimateAdmin(admin.ModelAdmin):
    list_display = ('state', 'rate_percent')

@admin.register(DealerCharge)
class DealerChargeAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'is_default_included')
