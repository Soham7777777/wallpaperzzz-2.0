from django.db import models
from django_stubs_ext.db.models import TypedModelMeta


class AbstractBaseModel(models.Model):
    objects: models.Manager["AbstractBaseModel"] = models.Manager()

    class Meta(TypedModelMeta):
        abstract = True
