from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test


def group_required(group_name):
    """Decorator to check if a user is in a specific group and return 403 if not."""
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.groups.filter(name=group_name).exists():
                return HttpResponseForbidden("You do not have permission to access this page.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator