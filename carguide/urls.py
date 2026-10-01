from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.urls import re_path
from django.views.static import serve

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

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

from django.http import HttpResponse
from django.core.management import call_command

def trigger_fix_taxes(request):
    try:
        call_command('fix_zero_taxes')
        return HttpResponse("Successfully updated zero taxes in the database! You can now test the calculator.")
    except Exception as e:
        return HttpResponse(f"Error: {e}")

urlpatterns += [
    path('api/fix-taxes/', trigger_fix_taxes),
]
