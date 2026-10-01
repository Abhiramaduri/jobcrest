from rest_framework.permissions import BasePermission

class isJobSeeker(BasePermission):
    def has_permission(self,request,view):
        return bool(
                request.user and request.user.is_authenticated and request.user.user_type=='jobseeker'
            )

class IsEmployer(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.user_type=='employer'
        )
