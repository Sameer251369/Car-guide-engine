from rest_framework import serializers
from .models import Lead

class LeadCreateSerializer(serializers.ModelSerializer):
    vehicle_id = serializers.IntegerField(write_only=True)
    state_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Lead
        fields = [
            'id', 'name', 'phone_number', 'city', 'state_id', 'vehicle_id',
            'ex_showroom_price_at_query', 'on_road_price_calculated',
            'source_page', 'created_at'
        ]

    def validate_phone_number(self, value):
        # Validate 10-digit Indian mobile number format (+91 or standard 10 digits starting with 6-9)
        cleaned = ''.join(filter(str.isdigit, str(value)))
        if len(cleaned) == 12 and cleaned.startswith('91'):
            cleaned = cleaned[2:]
        if len(cleaned) != 10 or not cleaned[0] in '6789':
            raise serializers.ValidationError("Please enter a valid 10-digit Indian mobile number.")
        return cleaned


class LeadAdminSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source='state.name', read_only=True, default='')

    class Meta:
        model = Lead
        fields = [
            'id', 'name', 'phone_number', 'city', 'state_name',
            'brand_snapshot', 'vehicle_name_snapshot',
            'ex_showroom_price_at_query', 'on_road_price_calculated',
            'source_page', 'created_at', 'is_exported', 'exported_at'
        ]
