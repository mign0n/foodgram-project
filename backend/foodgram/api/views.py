from djoser.views import UserViewSet as UserBaseViewSet
from recipes.models import User


class UserViewSet(UserBaseViewSet):
    queryset = User.objects.all().order_by('date_joined')
