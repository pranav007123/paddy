import os
import django
from django.conf import settings
from django.test import RequestFactory

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paddy.settings')
django.setup()

def get_response(request):
    from django.http import HttpResponse
    return HttpResponse("OK")

try:
    print("Testing Middleware Chain...")
    factory = RequestFactory()
    request = factory.get('/')

    # 1. Session Middleware
    print("1. Testing SessionMiddleware...")
    from django.contrib.sessions.middleware import SessionMiddleware
    session_middleware = SessionMiddleware(get_response)
    session_middleware.process_request(request)
    print("   SessionMiddleware OK.")

    # 2. Authentication Middleware
    print("2. Testing AuthenticationMiddleware...")
    from django.contrib.auth.middleware import AuthenticationMiddleware
    auth_middleware = AuthenticationMiddleware(get_response)
    auth_middleware.process_request(request)
    print("   AuthenticationMiddleware OK.")

    # 3. Message Middleware
    print("3. Testing MessageMiddleware...")
    from django.contrib.messages.middleware import MessageMiddleware
    msg_middleware = MessageMiddleware(get_response)
    msg_middleware.process_request(request)
    print("   MessageMiddleware OK.")

    # 4. CSRF Middleware
    print("4. Testing CsrfViewMiddleware...")
    from django.middleware.csrf import CsrfViewMiddleware
    csrf_middleware = CsrfViewMiddleware(get_response)
    res = csrf_middleware.process_request(request)
    if res: print("   CSRF rejected request (expected for no token)")
    else: print("   CsrfViewMiddleware OK.")

    print("All Middleware Tests Passed.")

except Exception as e:
    print("\n!!! EXCEPTION DETECTED !!!\n")
    import traceback
    traceback.print_exc()
