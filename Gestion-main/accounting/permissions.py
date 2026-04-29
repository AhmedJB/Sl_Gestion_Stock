from rest_framework import permissions


class IsAccountingUser(permissions.BasePermission):
    """
    Allows access only to users with is_accounting_user=True.
    """
    message = "Accounting access required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'is_accounting_user', False)
        )
