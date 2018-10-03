from rest_framework import permissions


class IsArticleOwnerOrReadOnly(permissions.BasePermission):
    """
    Use this class to restrict users from manipulating articles that do not belong to them

    It is an object-level permission that only allows owners of an object to edit it.

    """
    message = "You are not allowed to modify this article."

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        # so we'll always allow GET, HEAD or OPTIONS requests
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user
