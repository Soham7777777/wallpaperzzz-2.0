import uuid
from django.db import models
from django_stubs_ext.db.models import TypedModelMeta


class AbstractBaseModel(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    objects: models.Manager["AbstractBaseModel"] = models.Manager()

    class Meta(TypedModelMeta):
        abstract = True
