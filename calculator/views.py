from decimal import Decimal
from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from portfolio.models import Vehicle, VehicleVariant
from leads.models import Lead
from .models import State
from .serializers import StateSerializer, EstimateRequestSerializer, LeadCaptureRequestSerializer
from .services import calculate_on_road_price

class EstimateRateThrottle(AnonRateThrottle):
    scope = 'estimate'

class LeadRateThrottle(AnonRateThrottle):
    scope = 'leads'


def _resolve_variant_tier_label(variant_tier):
    return 'Top Variant' if variant_tier == 'top' else 'Starting Variant'


def _build_estimate_response(vehicle, state, breakdown, variant=None, variant_tier='start'):
    if variant:
        variant_name = variant.variant_name
    else:
        variant_name = _resolve_variant_tier_label(variant_tier)

    return {
        'vehicle_name': f"{vehicle.brand.name} {vehicle.name}",
        'variant_name': variant_name,
        'breakdown': breakdown,
    }


@api_view(['GET'])
def get_active_states(request):
    states = State.objects.filter(is_active=True)
    serializer = StateSerializer(states, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@throttle_classes([EstimateRateThrottle])
def calculate_estimate(request):
    serializer = EstimateRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    try:
        vehicle = Vehicle.objects.get(id=data['vehicle_id'], is_active=True)
        state = State.objects.get(id=data['state_id'], is_active=True)
    except (Vehicle.DoesNotExist, State.DoesNotExist):
        return Response({'error': 'Selected vehicle or state is invalid or inactive.'}, status=status.HTTP_404_NOT_FOUND)

    variant = None
    if data.get('variant_id'):
        try:
            variant = VehicleVariant.objects.get(id=data['variant_id'], vehicle=vehicle)
        except VehicleVariant.DoesNotExist:
            pass

    variant_tier = data.get('variant_tier', 'start')
    custom_ex_showroom = data.get('custom_ex_showroom')
    fuel_type = data.get('fuel_type') or (variant.fuel_type if variant and variant.fuel_type else vehicle.fuel_type)

    breakdown = calculate_on_road_price(
        vehicle=vehicle,
        state=state,
        fuel_type=fuel_type,
        ownership_type=data.get('ownership_type', 'individual'),
        variant=variant,
        variant_tier=variant_tier,
        custom_ex_showroom=custom_ex_showroom,
        is_financed=data.get('is_financed', False),
    )

    return Response(_build_estimate_response(vehicle, state, breakdown, variant, variant_tier))


@api_view(['POST'])
@throttle_classes([LeadRateThrottle])
def capture_lead_and_estimate(request):
    serializer = LeadCaptureRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    try:
        vehicle = Vehicle.objects.get(id=data['vehicle_id'], is_active=True)
        state = State.objects.get(id=data['state_id'], is_active=True)
    except (Vehicle.DoesNotExist, State.DoesNotExist):
        return Response({'error': 'Selected vehicle or state is invalid.'}, status=status.HTTP_404_NOT_FOUND)

    variant = None
    if data.get('variant_id'):
        try:
            variant = VehicleVariant.objects.get(id=data['variant_id'], vehicle=vehicle)
        except VehicleVariant.DoesNotExist:
            pass

    variant_tier = data.get('variant_tier', 'start')
    custom_ex_showroom = data.get('custom_ex_showroom')
    fuel_type = data.get('fuel_type') or (variant.fuel_type if variant and variant.fuel_type else vehicle.fuel_type)

    breakdown = calculate_on_road_price(
        vehicle=vehicle,
        state=state,
        fuel_type=fuel_type,
        ownership_type=data.get('ownership_type', 'individual'),
        variant=variant,
        variant_tier=variant_tier,
        custom_ex_showroom=custom_ex_showroom,
        is_financed=data.get('is_financed', False),
    )

    base_price = breakdown.get('ex_showroom_price') or Decimal('0.00')
    total_on_road = breakdown.get('total_on_road_price') or Decimal('0.00')
    full_vehicle_name = vehicle.name

    lead = Lead.objects.create(
        name=data['name'],
        phone_number=data['phone_number'],
        city=data['city'],
        state=state,
        vehicle=vehicle,
        brand_snapshot=vehicle.brand.name,
        vehicle_name_snapshot=full_vehicle_name,
        ex_showroom_price_at_query=base_price,
        on_road_price_calculated=total_on_road,
        source_page=data.get('source_page', 'calculator'),
    )

    response_data = _build_estimate_response(vehicle, state, breakdown, variant, variant_tier)
    response_data['lead_id'] = lead.id
    response_data['message'] = 'Lead captured successfully! Here is your itemized on-road price breakdown.'

    return Response(response_data, status=status.HTTP_201_CREATED)
