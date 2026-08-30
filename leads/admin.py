import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
from .models import Lead

@admin.action(description="Mark selected leads as exported to brands/dealers")
def mark_as_exported(modeladmin, request, queryset):
    queryset.update(is_exported=True, exported_at=timezone.now())

@admin.action(description="Export selected leads to CSV file")
def export_leads_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="car_guide_leads_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Name', 'Phone Number', 'City', 'State', 'Brand',
        'Vehicle', 'Ex-Showroom Price', 'Calculated On-Road Price',
        'Created At', 'Is Exported'
    ])
    for lead in queryset:
        writer.writerow([
            lead.id, lead.name, lead.phone_number, lead.city,
            lead.state.name if lead.state else '',
            lead.brand_snapshot, lead.vehicle_name_snapshot,
            lead.ex_showroom_price_at_query, lead.on_road_price_calculated,
            lead.created_at.strftime('%Y-%m-%d %H:%M'), lead.is_exported
        ])
    queryset.update(is_exported=True, exported_at=timezone.now())
    return response

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone_number', 'city', 'brand_snapshot', 'vehicle_name_snapshot', 'on_road_price_calculated', 'created_at', 'is_exported')
    list_filter = ('is_exported', 'brand_snapshot', 'state', 'created_at')
    search_fields = ('name', 'phone_number', 'city', 'brand_snapshot', 'vehicle_name_snapshot')
    readonly_fields = ('created_at', 'exported_at')
    actions = [mark_as_exported, export_leads_csv]
