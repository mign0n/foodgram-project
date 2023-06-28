from django.conf.urls import include
from django.urls import path

app_name = '%(app_label)s'

urlpatterns = [
    path('v1/', include('api.urls.v1'), name='v1'),
]
