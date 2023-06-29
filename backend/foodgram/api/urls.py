from django.urls import include, path

app_name = '%(app_label)s'

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
