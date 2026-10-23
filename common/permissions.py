from rest_framework.permissions import BasePermission


class IsObjectOwner(BasePermission):
    """
    Allow access only to the owner of an object.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id