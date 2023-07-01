from api.views import UserViewSet
from django.urls import include, path
from rest_framework.routers import SimpleRouter

app_name = '%(app_label)s'

users_router = SimpleRouter()
users_router.register('users', UserViewSet)

urlpatterns = [
    path('', include(users_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
