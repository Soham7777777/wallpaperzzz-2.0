from pathlib import PurePath
from django.db import models
from django.core import validators
from django.conf import settings
from common.validators import MaxFileSizeValidator
from common.utils import FileUploadPathGenerator
from common.regexes import name_regex_validator, key_regex_validator
from django_stubs_ext.db.models import TypedModelMeta
from adminapp.fields import WallpaperDimensionField


class Category(models.Model):

    name = models.CharField(
        blank=False,
        null=False,
        unique=True, 
        max_length=32,
        validators=[
            validators.MinLengthValidator(2),
            name_regex_validator,
        ],
    )
    thumbnail = models.ImageField(
        blank=False,
        null=False,
        unique=True,
        upload_to=FileUploadPathGenerator(PurePath('category_thumbnails'), 'thumbnail'),
        validators=[
            MaxFileSizeValidator(settings.MAX_FILE_SIZE),
            validators.FileExtensionValidator(('png',)),
        ],
    )

    objects: models.Manager["Category"] = models.Manager()


class WallpaperDimension(models.Model):
    
    width = WallpaperDimensionField()
    height = WallpaperDimensionField()

    objects: models.Manager["WallpaperDimension"] = models.Manager()


    class Meta(TypedModelMeta):
        constraints = [
            models.UniqueConstraint(fields=['width', 'height'], name="unique_width_height")
        ]


class SettingsStore(models.Model):
    
    key = models.CharField(
        primary_key=True,
        max_length=64,
        validators=[
            validators.MinLengthValidator(2),
            key_regex_validator,
        ]
    )
