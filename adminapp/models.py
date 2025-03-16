from pathlib import PurePath
from typing import cast
from django.db import models
from django.core import validators
from django.conf import settings
from common.validators import MaxFileSizeValidator, ImageFormatAndFileExtensionsValidator
from common.path_generators import FileUploadPathGenerator
from common.image_utils import ImageFormat
from common.regexes import name_regex_validator, key_regex_validator
from common.signals import SignalEffect
from common.models import AbstractBaseModel
from adminapp.fields import WallpaperDimensionField
from django.db.models.fields.files import ImageFieldFile
from django.core.exceptions import ValidationError
from django_stubs_ext.db.models.manager import RelatedManager
from wallpaperzzz.settings import kb


category_thumbnail_upload_path_generator = FileUploadPathGenerator(PurePath('category_thumbnails'), 'thumbnail')

wallpaper_image_upload_path_generator = FileUploadPathGenerator(PurePath('wallpapers'), 'wallpaper')

wallpaper_dummy_upload_path_generator = FileUploadPathGenerator(PurePath('wallpapers'), 'dummy')


def validate_image_max_file_size(value: ImageFieldFile) -> None:
    upper_limit = SettingsStore.settings.fetch_maximum_image_file_size_in_kb()
    MaxFileSizeValidator(upper_limit)(value)


class _SettingsManager(models.Manager["SettingsStore"]):

    def fetch_settings(self) -> "SettingsStore":
        return self.get_or_create(key='BASE_SETTINGS')[0]
    

    def fetch_maximum_image_file_size_in_kb(self) -> int:
        return self.fetch_settings().maximum_image_file_size * 1024


class SettingsStore(AbstractBaseModel):
    
    key = models.CharField(
        primary_key=True,
        max_length=64,
        validators=[
            validators.MinLengthValidator(2),
            key_regex_validator,
        ],
    )
    maximum_image_file_size = models.PositiveIntegerField(
        default=1024 * 5,
        validators=[
            validators.MinValueValidator(1),
            validators.MaxValueValidator(10 * 1024),
        ]
    )
    

    settings: _SettingsManager = _SettingsManager()


class Category(AbstractBaseModel):

    name = models.CharField(
        unique=True,
        max_length=32,
        validators=[
            validators.MinLengthValidator(2),
            name_regex_validator,
        ],
    )
    description = models.TextField(
        unique=True,
        max_length=512,
        validators=[
            validators.MinLengthValidator(2),
            validators.MaxLengthValidator(512),
        ]
    )
    thumbnail = models.ImageField(
        verbose_name=SignalEffect.AUTO_DELETE_FILE + SignalEffect.AUTO_DELETE_OLD_FILE,
        unique=True,
        upload_to=category_thumbnail_upload_path_generator,
        validators=[
            MaxFileSizeValidator(settings.MAX_FILE_SIZE),
            ImageFormatAndFileExtensionsValidator((ImageFormat.PNG, ImageFormat.JPEG, ImageFormat.WEBP))
        ],
        max_length=256,
    )

    wallpaper_groups: RelatedManager["WallpaperGroup"]
    
    objects: models.Manager["Category"] = models.Manager()


class WallpaperGroup(AbstractBaseModel):

    name = models.CharField(
        blank=True,
        max_length=64,
        validators=[
            name_regex_validator,
        ],
        default=''
    )
    description = models.TextField(
        blank=True,
        max_length=512,
        validators=[
            validators.MaxLengthValidator(512),
        ],
        default=''
    )
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='wallpaper_groups',
    )
    tags: RelatedManager["WallpaperTag"] = models.ManyToManyField( # type: ignore[assignment]
        "WallpaperTag",
        related_name="wallpaper_groups"
    )

    wallpapers: RelatedManager["Wallpaper"]

    objects: models.Manager["WallpaperGroup"] = models.Manager()


    # We will use the below clean method on model form and not on model instance
    # def clean(self) -> None:
    #     wallpapers = self.wallpapers.all()

    #     if not any(wallpapers):
    #         raise ValidationError(
    #             "Ensure that at least one wallpaper is uploaded.",
    #             code="wallpaper_required"
    #         )
        
    #     unique_dimensions = set()
    #     for wallpaper in wallpapers:
    #         dimension = wallpaper.dimension.width, wallpaper.dimension.height
    #         if dimension in unique_dimensions:
    #             raise ValidationError(
    #                 "Ensure that each wallpaper has unique dimension.",
    #                 code="duplicate_dimension"
    #             )
    #         unique_dimensions.add(dimension)


class Wallpaper(AbstractBaseModel):

    download_count = models.PositiveIntegerField(
        default=0,
    )
    image = models.ImageField(
        verbose_name=SignalEffect.AUTO_DELETE_FILE + SignalEffect.AUTO_DELETE_OLD_FILE,
        unique=True,
        upload_to=wallpaper_image_upload_path_generator,
        validators=[
            validate_image_max_file_size,
            ImageFormatAndFileExtensionsValidator((ImageFormat.JPEG, ))
        ],
        max_length=256,
    )
    dummy_image=models.ImageField(
        verbose_name=SignalEffect.AUTO_DELETE_FILE + SignalEffect.AUTO_DELETE_OLD_FILE,
        blank=True,
        upload_to=wallpaper_dummy_upload_path_generator,
        validators=[
            MaxFileSizeValidator(500 * kb),
            ImageFormatAndFileExtensionsValidator((ImageFormat.WEBP, ))
        ],
        max_length=256,
    )
    dimension = models.ForeignKey(
        "WallpaperDimension",
        on_delete=models.CASCADE,
        related_name='wallpapers',
    )
    wallpaper_group = models.ForeignKey(
        WallpaperGroup,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='wallpapers',
    )

    objects: models.Manager["Wallpaper"] = models.Manager()


    def clean(self) -> None:
        self.image = cast(ImageFieldFile, self.image)

        try:
            self.dimension = WallpaperDimension.objects.get(width=self.image.width, height=self.image.height)
        except WallpaperDimension.DoesNotExist:
            raise ValidationError(
                "Ensure the image dimensions match one of the allowed values, The current dimension: %(width)s x %(height)s is not supported.",
                code="invalid_image_dimensions",
                params={"width": str(self.image.width), "height": str(self.image.height)}
            )
    

class WallpaperDimension(AbstractBaseModel):
    
    width = WallpaperDimensionField()
    height = WallpaperDimensionField()


    class Meta(AbstractBaseModel.Meta):
        constraints = [
            models.UniqueConstraint(fields=['width', 'height'], name="unique_width_height")
        ]

    wallpapers: RelatedManager["Wallpaper"]

    objects: models.Manager["WallpaperDimension"] = models.Manager()


class WallpaperTag(AbstractBaseModel):

    value = models.CharField(
        max_length=32,
        validators=[
            validators.MinLengthValidator(2),
            name_regex_validator,
        ]
    )

    wallpaper_groups: RelatedManager[WallpaperGroup]

    objects: models.Manager["WallpaperTag"] = models.Manager()
