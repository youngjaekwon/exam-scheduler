from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrOwnerWithEditableCondition(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user:
            return False

        if request.user.is_staff:
            return True

        if obj.user != request.user:
            return False

        if request.method in SAFE_METHODS:
            return True

        return not obj.is_confirmed
