from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from loguru import logger
from rest_framework import exceptions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import as_serializer_error
from rest_framework.views import exception_handler as exception_handler_

from .exception import ApplicationError


def exception_handler(exc, ctx):
    """
    参考自Django-Styleguide
    {
        "message": "Error message",
        "extra": {}
    }
    """
    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))

    if isinstance(exc, Http404):
        exc = exceptions.NotFound()

    if isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    response = exception_handler_(exc, ctx)

    # If unexpected error occurs (server error, etc.)
    if response is None:
        if isinstance(exc, ApplicationError):
            data = {"message": exc.message, "extra": exc.extra}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        logger.exception(exc)

        data = {"message": _("服务器开了小差, 请稍后再试"), "extra": {}}
        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if isinstance(exc.detail, (list, dict)):
        response.data = {"detail": response.data}

    if isinstance(exc, exceptions.ValidationError):
        response.data["message"] = _("Validation error")
        response.data["extra"] = {"fields": response.data["detail"]}  # noqa
    else:
        if isinstance(response.data["detail"], dict) and "detail" in response.data["detail"]:
            response.data["message"] = response.data["detail"]["detail"]
        else:
            response.data["message"] = response.data["detail"]
        response.data["extra"] = {}

    del response.data["detail"]

    return response
