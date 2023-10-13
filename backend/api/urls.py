from api import views
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
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
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        views.CartViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
        name='cart',
    ),
    path('auth/', include('djoser.urls.authtoken')),
    path('docs/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'docs/swagger-ui/',
        SpectacularSwaggerView.as_view(url_name='api:schema'),
        name='swagger-ui',
    ),
]
