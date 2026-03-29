from urllib import request

from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.utils import timezone
from datetime import timedelta

class IsOwner(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsAnonymous(BasePermission):

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
    

class CanEditWithin15Minutes(BasePermission):
    def has_object_permission(self, request, view, obj):
        time_passed = timezone.now() - obj.created_at
        return time_passed <= timedelta(minutes=30)
    
class IsModerator(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET', 'PUT', 'PATCH', 'DELETE']:
            return request.user and request.user.is_authenticated and request.user.is_staff
        elif request.method == 'POST':
            return not(request.user and request.user.is_authenticated and request.user.is_staff)
        
