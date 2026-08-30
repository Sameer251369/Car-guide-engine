from rest_framework.routers import DefaultRouter
from .views import AdminVehicleWorklistViewSet

router = DefaultRouter()
router.register(r'', AdminVehicleWorklistViewSet, basename='admin-vehicle')

urlpatterns = router.urls
