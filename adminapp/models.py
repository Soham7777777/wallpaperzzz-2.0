from pathlib import PurePath
from django.db import models
from django.core import validators
from django.conf import settings
from adminapp.validators import MaxFileSizeValidator
from adminapp.utils import FileUploadPathGenerator
from django_stubs_ext.db.models import TypedModelMeta
from adminapp.fields import WallpaperDimensionField


NAME_REGEX = r"^(?!.*\s{2,})[A-Za-z]+(?: [A-Za-z]+)*$", "Ensure that the name contains only English letters or spaces, with no leading or trailing spaces and no consecutive spaces."
KEY_REGEX = r"^[A-Z]+(?:_[A-Z]+)*$", "Ensure that the key contains only uppercase English letters or underscores, with no leading or trailing underscores and no consecutive underscores."


class Category(models.Model):

    name = models.CharField(
        blank=False,
        null=False,
        unique=True, 
        max_length=32,
        validators=[
            validators.MinLengthValidator(2),
            validators.RegexValidator(*NAME_REGEX),
        ],
    )
    thumbnail = models.ImageField(
        blank=False,
        null=False,
        unique=True,
        upload_to=FileUploadPathGenerator(base_path=PurePath('category_thumbnails'), name_prefix='thumbnail'),
        validators=[
            MaxFileSizeValidator(max_file_size=settings.MAX_FILE_SIZE),
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
            validators.RegexValidator(*KEY_REGEX),
        ]
    )
