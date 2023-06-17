from django.db import models

from base.id_generator import id_gen


class BaseModel(models.Model):
    id = models.BigIntegerField(primary_key=True, default=id_gen.next_id)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False)

    class Meta:
        abstract = True
