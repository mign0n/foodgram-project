from django.db.models import Model
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(
        self,
        request: Request,
        view: ModelViewSet,
        obj: Model,
    ) -> bool:
        del view
        return bool(
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user,
        )
