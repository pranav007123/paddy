from django.shortcuts import redirect
from django.contrib import messages
from paddy.models import user as PaddyUser

def get_current_user_obj(request):
    uid = request.session.get('uid')
    if uid:
        try:
            return PaddyUser.objects.get(id=uid)
        except PaddyUser.DoesNotExist:
            return None
    return None

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        user = get_current_user_obj(request)
        if not user:
            return redirect('login')
        
        if not user.is_superuser:
            messages.error(request, 'Access denied. Admin rights required.')
            return redirect('shop_dashboard')
            
        return view_func(request, *args, **kwargs)
    return wrapper
