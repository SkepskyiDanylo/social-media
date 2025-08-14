from rest_framework.permissions import BasePermission, SAFE_METHODS


class PostPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in SAFE_METHODS:
            return user.is_authenticated
        return obj.author == user


class CanDeleteComment(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method == "DELETE":
            return user.is_authenticated and user == obj.author or user == obj.post.author
        return user.is_authenticated
