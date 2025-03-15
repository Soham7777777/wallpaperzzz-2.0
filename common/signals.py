from typing import Any, cast
from django.db import models
from django.db.models.fields.files import FieldFile
from enum import StrEnum, auto
from common.models import AbstractBaseModel


class SignalEffect(StrEnum):
    AUTO_DELETE_FILE = auto()
    AUTO_DELETE_OLD_FILE = auto()


def delete_file_post_delete_function(sender: type[AbstractBaseModel], **kwargs: Any) -> None: 
    instance = cast(AbstractBaseModel, kwargs['instance'])
    for file_field in instance._meta.get_fields():
        if isinstance(file_field, models.FileField) and SignalEffect.AUTO_DELETE_FILE in file_field.verbose_name:
            file = cast(FieldFile, getattr(instance, file_field.get_attname()))
            file.delete(save=False)
        

def delete_old_file_pre_save_function(sender: type[AbstractBaseModel], **kwargs: Any) -> None:
    instance = cast(AbstractBaseModel, kwargs['instance'])
    pk_val = getattr(instance, instance._meta.pk.get_attname())
    if pk_val is not None:
        for file_field in instance._meta.get_fields():
            if isinstance(file_field, models.FileField) and SignalEffect.AUTO_DELETE_OLD_FILE in file_field.verbose_name:
                old_file = cast(FieldFile, getattr(sender.objects.get(pk=pk_val), file_field.get_attname()))
                current_file = cast(FieldFile, getattr(instance, file_field.get_attname()))
                if current_file.name != old_file.name:
                    old_file.delete(save=False)
