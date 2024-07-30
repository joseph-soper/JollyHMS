from rest_framework import permissions

class IsGuest(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.userprofile.role.name == 'Guest'
    
class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.userprofile.role.name in ['Staff', 'Manager', 'Admin']
    
class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.userprofile.role.name in ['Manager', 'Admin']
    
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.userprofile.role.name == 'Admin'
