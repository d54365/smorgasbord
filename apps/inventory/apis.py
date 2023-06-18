from rest_framework import viewsets
from rest_framework.decorators import action

from .services import InventoryService
from .models import Inventory
from base.exceptions.exception import ApplicationError
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response


class InventoryViewSet(viewsets.ViewSet):
    @action(methods=["PUT"], detail=True, url_path="deduct")
    def deduct(self, request, pk):
        try:
            instance: Inventory = InventoryService.get_inventory_by_pk(pk)
        except Inventory.DoesNotExist:
            raise ApplicationError(message=_("not found"))
        if instance.quantity < 1:
            raise ApplicationError(message=_("库存不足"))
        InventoryService.deduct(instance.id, 1)
        return Response()
