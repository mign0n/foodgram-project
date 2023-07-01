from api import serializers
from djoser.views import UserViewSet as UserBaseViewSet
from recipes.models import Tag, User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class UserViewSet(UserBaseViewSet):
    queryset = User.objects.all().order_by('date_joined')


class TagViewSet(viewsets.ModelViewSet):
    pagination_class = None
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Tag.objects.all().order_by('id')
    serializer_class = serializers.TagSerializer
