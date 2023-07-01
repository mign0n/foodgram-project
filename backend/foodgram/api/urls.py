from api.views import RecipeViewSet, TagViewSet, UserViewSet
from django.urls import include, path
from rest_framework.routers import SimpleRouter

app_name = '%(app_label)s'

router = SimpleRouter()
router.register('users', UserViewSet)
router.register('tags', TagViewSet, basename='tag')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
