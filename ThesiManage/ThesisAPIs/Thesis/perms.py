from rest_framework import permissions
from rest_framework.permissions import BasePermission

from .models import User


class IsAuthenticated(BasePermission):
    message = "Bạn không có quyền truy cập tài nguyên này!"

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        return request.user.is_authenticated


class IsAdmin(BasePermission):
    message = "Bạn không có quyền truy cập tài nguyên này!"

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        return bool(request.user.role == "admin")


class IsMinistryAuthenticated(BasePermission):
    message = "Bạn không có quyền truy cập tài nguyên này!"

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        return bool(request.user.role == "ministry")
