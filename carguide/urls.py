from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('carguide.auth_urls')),
    path('api/v1/brands/', include('portfolio.urls_brands')),
    path('api/v1/vehicles/', include('portfolio.urls_vehicles')),
    path('api/v1/blog/', include('blog.urls')),
    path('api/v1/calculator/', include('calculator.urls')),
    path('api/v1/admin/leads/', include('leads.urls')),
    path('api/v1/admin/vehicles/', include('portfolio.urls_admin_vehicles')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
