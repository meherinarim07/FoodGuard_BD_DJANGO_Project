from django.contrib import messages
from django.shortcuts import redirect


def role_required(*roles):
    # usage: @role_required('verifier', 'authority')
    def decorator(view):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.userprofile.role not in roles:
                messages.error(request, 'You do not have permission to open that page.')
                return redirect('home')
            return view(request, *args, **kwargs)
        return wrapper
    return decorator