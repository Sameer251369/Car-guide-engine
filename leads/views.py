import csv
from rest_framework import viewsets, mixins, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.http import HttpResponse
from .models import Lead
from .serializers import LeadAdminSerializer

class AdminLeadViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadAdminSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_exported', 'brand_snapshot', 'state']
    search_fields = ['name', 'phone_number', 'city', 'brand_snapshot', 'vehicle_name_snapshot']
    ordering_fields = ['created_at', 'on_road_price_calculated']
    ordering = ['-created_at']

    @action(detail=False, methods=['post'])
    def mark_exported(self, request):
        lead_ids = request.data.get('lead_ids', [])
        if not lead_ids:
            return Response({'error': 'lead_ids array is required'}, status=status.HTTP_400_BAD_REQUEST)

        updated_count = Lead.objects.filter(id__in=lead_ids).update(
            is_exported=True,
            exported_at=timezone.now(),
        )
        return Response({'message': f'Successfully marked {updated_count} leads as exported'})

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export leads as CSV. Optional ?is_exported=false to filter unexported only."""
        queryset = self.filter_queryset(self.get_queryset())

        is_exported = request.query_params.get('is_exported')
        if is_exported is not None:
            queryset = queryset.filter(is_exported=is_exported.lower() in ('true', '1', 'yes'))

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="car_guide_leads.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Name', 'Phone', 'City', 'State', 'Brand', 'Vehicle',
            'Ex-Showroom Price', 'On-Road Price', 'Source Page',
            'Created At', 'Is Exported', 'Exported At',
        ])

        for lead in queryset:
            writer.writerow([
                lead.id,
                lead.name,
                lead.phone_number,
                lead.city,
                lead.state.name if lead.state else '',
                lead.brand_snapshot,
                lead.vehicle_name_snapshot,
                lead.ex_showroom_price_at_query,
                lead.on_road_price_calculated,
                lead.source_page,
                lead.created_at.isoformat() if lead.created_at else '',
                lead.is_exported,
                lead.exported_at.isoformat() if lead.exported_at else '',
            ])

        return response
