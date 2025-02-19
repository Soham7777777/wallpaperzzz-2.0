from typing import Any, cast
from adminapp.models import Category
from django.db.models.fields.files import FieldFile


def delete_category_thumbnail(sender: type[Category], **kwargs: Any) -> None: 
    category_instance = cast(Category, kwargs['instance'])
    thumbnail = cast(FieldFile, category_instance.thumbnail)
    thumbnail.delete(False)
