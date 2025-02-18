from typing import Any, cast
from django.db import models
from django.dispatch import receiver
from adminapp.models import Category
from django.db.models.fields.files import FieldFile


@receiver(models.signals.post_delete, sender=Category, dispatch_uid='delete_category_thumbnail')
def delete_category_thumbnail(sender: type[Category], **kwargs: Any) -> None: 
    category_instance = cast(Category, kwargs['instance'])
    thumbnail = cast(FieldFile, category_instance.thumbnail)
    thumbnail.delete(False)
