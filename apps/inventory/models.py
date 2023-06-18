from base.utils.base_model import BaseModel
from django.db import models


class Inventory(BaseModel):
    quantity = models.IntegerField(verbose_name="库存数量")
    product_code = models.IntegerField()
    warehouse = models.CharField(max_length=128)

    class Meta:
        db_table = "inventory_inventory"
