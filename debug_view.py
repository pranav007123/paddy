import os
import django
from django.conf import settings
from django.test import RequestFactory

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paddy.settings')
django.setup()

from paddy.views import first

try:
    print("Simulating request to 'first' view...")
    factory = RequestFactory()
    request = factory.get('/')
    
    # Add session to request manually since middleware isn't running
    from django.contrib.sessions.backends.db import SessionStore
    request.session = SessionStore()

    response = first(request)
    print("View returned status:", response.status_code)
except Exception as e:
    import traceback
    traceback.print_exc()
