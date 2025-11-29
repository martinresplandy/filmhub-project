from rest_framework import permissions

# Allows read access (GET, HEAD, OPTIONS) to everyone.
# Allows write/modify access (POST, PUT, PATCH, DELETE) only to superusers.
class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission that allows read-only access for any request,
    but only permits write access to superusers.
    """

    # Method called to check permission at the VIEW level (ViewSet)
    def has_permission(self, request, view):
        # 1. Read (GET, HEAD, OPTIONS)
        # If the HTTP method is in SAFE_METHODS (read-only methods), allow access
        if request.method in permissions.SAFE_METHODS:
            return True  # Allow anyone to read

        # 2. Write (POST, PUT, PATCH, DELETE)
        # For write methods, check that the user is a superuser.
        # The user should already be authenticated (e.g. via TokenAuthentication/IsAuthenticated),
        # but this enforces the higher-level permission.
        return bool(request.user and request.user.is_superuser)