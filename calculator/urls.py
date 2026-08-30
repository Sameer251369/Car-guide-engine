from django.urls import path
from .views import get_active_states, calculate_estimate, capture_lead_and_estimate

urlpatterns = [
    path('states/', get_active_states, name='calculator-states'),
    path('estimate/', calculate_estimate, name='calculator-estimate'),
    path('lead/', capture_lead_and_estimate, name='calculator-lead'),
]
