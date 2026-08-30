from django.db import models
from portfolio.models import Vehicle
from calculator.models import State

class Lead(models.Model):
    name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, related_name='leads')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='leads')
    
    # Snapshot fields for historical accuracy & reselling integrity
    brand_snapshot = models.CharField(max_length=100)
    vehicle_name_snapshot = models.CharField(max_length=150)
    ex_showroom_price_at_query = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    on_road_price_calculated = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    source_page = models.CharField(max_length=100, default='calculator')
    created_at = models.DateTimeField(auto_now_add=True)
    is_exported = models.BooleanField(default=False)
    exported_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Lead: {self.name} ({self.phone_number}) - {self.brand_snapshot} {self.vehicle_name_snapshot}"
