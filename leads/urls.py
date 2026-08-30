from rest_framework.routers import DefaultRouter
from .views import AdminLeadViewSet

router = DefaultRouter()
router.register(r'', AdminLeadViewSet, basename='admin-lead')

urlpatterns = router.urls
