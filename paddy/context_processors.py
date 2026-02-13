from .models import user

def user_context(request):
    """
    Makes the logged-in user object available globally in templates as 'current_user'.
    """
    if 'uid' in request.session:
        try:
            return {'current_user': user.objects.get(id=request.session['uid'])}
        except user.DoesNotExist:
            pass
    elif request.session.get('details') == 'admin':
        # Return a mock user object for the hardcoded admin
        class AdminUser:
            name = "Executive Administrator"
            is_superuser = True
            profile_pic = None
        return {'current_user': AdminUser()}
    return {'current_user': None}
