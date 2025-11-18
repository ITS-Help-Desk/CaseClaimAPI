from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test


# Role hierarchy - higher number = higher permissions
ROLE_HIERARCHY = {
    'Tech': 1,
    'Lead': 2,
    'Phone Analyst': 3,
    'Manager': 4
}


def get_user_highest_role_level(user):
    """Get the highest role level for a user based on hierarchy."""
    user_groups = user.groups.values_list('name', flat=True)
    max_level = 0
    
    for group_name in user_groups:
        level = ROLE_HIERARCHY.get(group_name, 0)
        if level > max_level:
            max_level = level
    
    return max_level


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


def role_required(minimum_role):
    """
    Decorator to check if user has at least the specified role level based on hierarchy.
    
    Example:
        @role_required('Lead')  # Allows Lead, Phone Analyst, and Manager
        def my_view(request):
            ...
    
    Role hierarchy (lowest to highest):
        Tech < Lead < Phone Analyst < Manager
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            minimum_level = ROLE_HIERARCHY.get(minimum_role, 0)
            user_level = get_user_highest_role_level(request.user)
            
            if user_level < minimum_level:
                return HttpResponseForbidden(
                    f"You do not have permission to access this page. "
                    f"Requires at least '{minimum_role}' role."
                )
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator