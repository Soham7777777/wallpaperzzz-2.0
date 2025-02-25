from typing import Any, cast
from adminapp.models import Category
from django.db.models.fields.files import ImageFieldFile


def delete_category_thumbnail(sender: type[Category], **kwargs: Any) -> None: 
    instance = cast(Category, kwargs['instance'])
    thumbnail = cast(ImageFieldFile, instance.thumbnail)
    thumbnail.delete(False)


def delete_old_category_thumbnail(sender: type[Category], **kwargs: Any) -> None:
    instance = cast(Category, kwargs["instance"])
    if instance.id is not None:
        old_thumbnail = cast(ImageFieldFile, Category.objects.get(pk=instance.id).thumbnail) 
        old_thumbnail.delete(False)
