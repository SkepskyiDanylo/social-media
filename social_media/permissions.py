from rest_framework.permissions import BasePermission


class CanDeleteComment(BasePermission):
    def has_object_permission(self, request, view, comment):
        user = request.user
        return (
            user.is_authenticated
            and user == comment.user
            or user == comment.post.user
            or user.is_staff
        )
