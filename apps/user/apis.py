from django.core.cache import cache
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from base.auth.backends import JWTAuthentication
from .serializers import (
    UserCenterOutputSerializer,
    SendMailInputSerializer,
    ActivateMailInputSerializer,
)
from .tasks import send_email_active


class UserViewSet(viewsets.ViewSet):
    authentication_classes = (JWTAuthentication,)

    @action(methods=["GET"], detail=False, url_path="v1/center")
    def center(self, request):
        serializer = UserCenterOutputSerializer(instance=request.user)
        return Response(serializer.data)

    @action(methods=["PUT"], detail=False, url_path="v1/mail/(?P<mail>.*)")
    def send_activate_mail(self, request, mail):
        serializer = SendMailInputSerializer(data={"mail": mail}, instance=request.user)
        serializer.is_valid(raise_exception=True)
        request.user.mail = mail
        request.user.mail_active = False
        request.user.save()

        send_email_active.delay(request.user.id, mail)

        return Response()

    @action(methods=["GET"], detail=False, url_path="v1/activate/(?P<token>.*)", authentication_classes=[])
    def activate_mail(self, request, token):
        serializer = ActivateMailInputSerializer(data={"token": token})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        user.mail_active = True
        user.mail_active_at = timezone.now()
        user.save()

        cache.delete(serializer.validated_data["key"])

        return Response()
