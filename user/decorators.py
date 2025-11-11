from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test


def group_required(group_names):
    """Decorator to check if a user is in any of the specified groups and return 403 if not."""
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if isinstance(group_names, str):
                groups = [group_names]
            else:
                groups = group_names

            if not any(request.user.groups.filter(name=group).exists() for group in groups):
                return HttpResponseForbidden("You do not have permission to access this page.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator