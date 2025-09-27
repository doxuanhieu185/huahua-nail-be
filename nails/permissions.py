from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """
    Chỉ cho phép truy cập nếu người dùng là admin
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin()
