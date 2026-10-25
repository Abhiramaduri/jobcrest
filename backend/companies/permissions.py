from rest_framework.permissions import BasePermission,SAFE_METHODS

class IsJobSeeker(BasePermission):
    def has_permission(self,request,view):
        return bool(
            request.user and request.user.is_authenticated and request.user.user_type=='jobseeker'
        )
class IsEmployer(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.user_type=='employer'
        )
class IsCompanyOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.created_by==request.user