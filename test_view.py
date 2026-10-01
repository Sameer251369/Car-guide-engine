import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carguide.settings')
django.setup()

from django.test.client import RequestFactory
from carguide.urls import trigger_fix_taxes

rf = RequestFactory()
request = rf.get('/api/fix-taxes/')
response = trigger_fix_taxes(request)
print("STATUS CODE:", response.status_code)
print("CONTENT:", response.content)
