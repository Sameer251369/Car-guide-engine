from rest_framework import serializers
from .models import State

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name', 'code', 'price_basis', 'registration_fee', 'smart_card_fee', 'hsrp_fee', 'hypothecation_fee', 'fastag_fee']


class EstimateRequestSerializer(serializers.Serializer):
    vehicle_id = serializers.IntegerField()
    state_id = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    variant_tier = serializers.ChoiceField(choices=['start', 'top'], default='start')
    custom_ex_showroom = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    fuel_type = serializers.CharField(required=False, allow_blank=True)
    ownership_type = serializers.ChoiceField(choices=['individual', 'company'], default='individual')
    is_financed = serializers.BooleanField(default=False)


class LeadCaptureRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    phone_number = serializers.CharField(max_length=20)
    city = serializers.CharField(max_length=100)
    vehicle_id = serializers.IntegerField()
    state_id = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    variant_tier = serializers.ChoiceField(choices=['start', 'top'], default='start')
    custom_ex_showroom = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    fuel_type = serializers.CharField(required=False, allow_blank=True)
    ownership_type = serializers.ChoiceField(choices=['individual', 'company'], default='individual')
    is_financed = serializers.BooleanField(default=False)
    source_page = serializers.CharField(max_length=100, default='calculator')

    def validate_phone_number(self, value):
        cleaned = ''.join(filter(str.isdigit, str(value)))
        if len(cleaned) == 12 and cleaned.startswith('91'):
            cleaned = cleaned[2:]
        if len(cleaned) != 10 or not cleaned[0] in '6789':
            raise serializers.ValidationError("Please enter a valid 10-digit Indian mobile number.")
        return cleaned
