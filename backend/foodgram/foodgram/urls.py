from django.apps import apps
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'api/',
        include('api.urls', namespace=apps.get_app_config('api').name),
        name='api',
    ),
]
