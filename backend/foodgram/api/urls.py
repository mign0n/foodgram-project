from api import views
from django.urls import include, path
from rest_framework.routers import SimpleRouter

app_name = '%(app_label)s'

router = SimpleRouter()
router.register('users', views.UserViewSet)
router.register('tags', views.TagViewSet, basename='tag')
router.register('recipes', views.RecipeViewSet, basename='recipes')
router.register('ingredients', views.IngredientViewSet, basename='ingredient')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'recipes/<int:recipe_id>/favorite/',
        views.FavoriteViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
        name='favorite',
    ),
    path('auth/', include('djoser.urls.authtoken')),
]
