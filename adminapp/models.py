from pathlib import PurePath
from django.db import models
from django.core import validators
from django.conf import settings
from common.validators import MaxFileSizeValidator
from common.utils import FileUploadPathGenerator
from common.regexes import name_regex_validator, key_regex_validator
from common.signals import SignalEffect
from common.models import AbstractBaseModel
from adminapp.fields import WallpaperDimensionField


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
            validators.FileExtensionValidator(('png', 'apng')),
        ],
    )


class WallpaperDimension(AbstractBaseModel):
    
    width = WallpaperDimensionField()
    height = WallpaperDimensionField()


    class Meta(AbstractBaseModel.Meta):
        constraints = [
            models.UniqueConstraint(fields=['width', 'height'], name="unique_width_height")
        ]


class _SettingsManager(models.Manager["SettingsStore"]):
    
    def get(self) -> "SettingsStore":
        return self.get_or_create(key='BASE_SETTINGS')[0]


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
    
    settings: models.Manager["SettingsStore"] = _SettingsManager()


class AllowedImageExtensions(AbstractBaseModel):
    
    settings_store = models.OneToOneField(
        SettingsStore,
        on_delete=models.CASCADE,
        related_name='allowed_image_extensions',
        primary_key=True
    )
    # png = models.BooleanField(
    #     blank=False,
    #     null=False,
    #     default=True
    # )
    # png = models.BooleanField(
    #     blank=False,
    #     null=False,
    #     default=True
    # )
    # png = models.BooleanField(
    #     blank=False,
    #     null=False,
    #     default=True
    # )
    # png = models.BooleanField(
    #     blank=False,
    #     null=False,
    #     default=True
    # )


class WallpaperGroup(AbstractBaseModel):
    pass


class Wallpaper(AbstractBaseModel):

    image = models.ImageField(
        verbose_name=SignalEffect.AUTO_DELETE_FILE + SignalEffect.AUTO_DELETE_OLD_FILE,
        blank=False,
        null=False,
        unique=True,
        upload_to=FileUploadPathGenerator(PurePath('wallpapers'), 'wallpaper'),
        validators=[
            MaxFileSizeValidator(settings.MAX_FILE_SIZE),
            validators.FileExtensionValidator(('png',)),
        ],
    )


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
