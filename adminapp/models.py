from pathlib import PurePath
from typing import Self
from django.db import models
from django.core import validators
from django.conf import settings
from common.validators import MaxFileSizeValidator, ImageTypeFileExtensionsValidator
from common.utils import FileUploadPathGenerator, ImageType, get_file_extensions_for_image_type
from common.regexes import name_regex_validator, key_regex_validator
from common.signals import SignalEffect
from common.models import AbstractBaseModel
from adminapp.fields import WallpaperDimensionField
from django.db.models.fields.files import ImageFieldFile


class _SettingsManager(models.Manager["SettingsStore"]):

    def fetch_settings(self: Self) -> "SettingsStore":
        return self.get_or_create(key='BASE_SETTINGS')[0]


    def fetch_allowed_image_file_extensions(self) -> tuple[str, ...]:
        settings = self.fetch_settings()
        allowed_image_file_extensions: list[str] = []

        for field in SettingsStore._meta.get_fields():
            if (isinstance(field, models.BooleanField)) and (field.db_column in ImageType) and (getattr(settings, field.name) is True):
                allowed_image_file_extensions += [
                    *get_file_extensions_for_image_type(getattr(ImageType, str(field.db_column)))
                ]
        
        return tuple(allowed_image_file_extensions)


class Category(AbstractBaseModel):

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
        verbose_name=SignalEffect.AUTO_DELETE_FILE + SignalEffect.AUTO_DELETE_OLD_FILE,
        blank=False,
        null=False,
        unique=True,
        upload_to=FileUploadPathGenerator(PurePath('category_thumbnails'), 'thumbnail'),
        validators=[
            MaxFileSizeValidator(settings.MAX_FILE_SIZE),
            ImageTypeFileExtensionsValidator((ImageType.PNG, ImageType.JPEG))
        ],
    )


class WallpaperGroup(AbstractBaseModel):
    pass


class Wallpaper(AbstractBaseModel):

    @staticmethod
    def _validate_image_max_file_size(value: ImageFieldFile) -> None:
        upper_limit = SettingsStore.settings.fetch_settings().maximum_image_file_size * 1024
        MaxFileSizeValidator(upper_limit)(value)
    

    @staticmethod
    def _validate_image_file_extensions(value: ImageFieldFile) -> None:
        extensions = SettingsStore.settings.fetch_allowed_image_file_extensions()
        validators.FileExtensionValidator(extensions)(value)


    image = models.ImageField(
        verbose_name=SignalEffect.AUTO_DELETE_FILE + SignalEffect.AUTO_DELETE_OLD_FILE,
        blank=False,
        null=False,
        unique=True,
        upload_to=FileUploadPathGenerator(PurePath('wallpapers'), 'wallpaper'),
        validators=[
            _validate_image_max_file_size,
            _validate_image_file_extensions
        ],
    )
    

class WallpaperDimension(AbstractBaseModel):
    
    width = WallpaperDimensionField()
    height = WallpaperDimensionField()


    class Meta(AbstractBaseModel.Meta):
        constraints = [
            models.UniqueConstraint(fields=['width', 'height'], name="unique_width_height")
        ]


class WallpaperTag(AbstractBaseModel):

    value = models.CharField(
        blank=False,
        null=False,
        max_length=32,
        validators=[
            validators.MinLengthValidator(2),
            name_regex_validator,
        ]
    )
    wallpaper_group = models.ForeignKey(
        WallpaperGroup,
        on_delete=models.CASCADE,
        related_name='tags',
    )


class SettingsStore(AbstractBaseModel):
    
    key = models.CharField(
        primary_key=True,
        max_length=64,
        validators=[
            validators.MinLengthValidator(2),
            key_regex_validator,
        ]
    )
    maximum_image_file_size = models.PositiveIntegerField(
        blank=False,
        null=False,
        default=1024,
        validators=[
            validators.MinValueValidator(1),
            validators.MaxValueValidator(10 * 1024),
        ]
    )
    compress_image_on_upload = models.BooleanField(
        blank=False,
        null=False,
        default=True
    )
    png = models.BooleanField(
        blank=False,
        null=False,
        default=True,
        db_column=ImageType.PNG,
    )
    jpeg = models.BooleanField(
        blank=False,
        null=False,
        default=True,
        db_column=ImageType.JPEG,
    )
    webp = models.BooleanField(
        blank=False,
        null=False,
        default=True,
        db_column=ImageType.WEBP,
    )

    settings: _SettingsManager = _SettingsManager()
