from api.views import TagViewSet, UserViewSet
from django.urls import include, path
from rest_framework.routers import SimpleRouter

app_name = '%(app_label)s'

router = SimpleRouter()
router.register('users', UserViewSet)
router.register('tags', TagViewSet, basename='tag')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
