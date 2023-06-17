from django.conf import settings
from rest_framework import routers

from account import apis as account_apis
from user import apis as users_apis

if settings.DEBUG:
    router = routers.DefaultRouter()
else:
    router = routers.SimpleRouter()


router.register("api/account", account_apis.AccountViewSet, basename="account")
router.register("api/user", users_apis.UserViewSet, basename="user")
