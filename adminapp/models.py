from pathlib import PurePath
from typing import cast
from django.db import models
from django.core import validators
from django.conf import settings
from common.validators import MaxFileSizeValidator, ImageFormatAndFileExtensionsValidator
from common.utils import FileUploadPathGenerator, ImageFormat, generate_thumbnail_webp_from_jpeg, generate_dummy_webp_from_jpeg
from common.regexes import name_regex_validator, key_regex_validator
from common.signals import SignalEffect
from common.models import AbstractBaseModel
from adminapp.fields import WallpaperDimensionField
from django.db.models.fields.files import ImageFieldFile
from django.core.exceptions import ValidationError
from django_stubs_ext.db.models.manager import RelatedManager
from wallpaperzzz.settings import kb
from django.core.files.images import ImageFile


category_thumbnail_upload_path_generator = FileUploadPathGenerator(PurePath('category_thumbnails'), 'thumbnail')

wallpaper_image_upload_path_generator = FileUploadPathGenerator(PurePath('wallpapers'), 'wallpaper')

wallpaper_thumbnail_upload_path_generator = FileUploadPathGenerator(PurePath('wallpapers'), 'thumbnail')

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
        blank=False,
        null=False,
        default=1024 * 5,
        validators=[
            validators.MinValueValidator(1),
            validators.MaxValueValidator(10 * 1024),
        ]
    )
    

    settings: _SettingsManager = _SettingsManager()


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
    description = models.TextField(
        blank=False,
        null=False,
        unique=True,
        max_length=512,
        validators=[
            validators.MinLengthValidator(2),
            validators.MaxLengthValidator(512),
        ]
    )
    thumbnail = models.ImageField(
        verbose_name=SignalEffect.AUTO_DELETE_FILE + SignalEffect.AUTO_DELETE_OLD_FILE,
        blank=False,
        null=False,
        unique=True,
        upload_to=category_thumbnail_upload_path_generator,
        validators=[
            MaxFileSizeValidator(settings.MAX_FILE_SIZE),
            ImageFormatAndFileExtensionsValidator((ImageFormat.PNG, ImageFormat.JPEG, ImageFormat.WEBP))
        ],
    )

    wallpaper_groups: RelatedManager["WallpaperGroup"]
    
    objects: models.Manager["Category"] = models.Manager()


class WallpaperGroup(AbstractBaseModel):

    name = models.CharField(
        blank=False,
        null=True,
        max_length=64,
        validators=[
            validators.MinLengthValidator(2),
            name_regex_validator,
        ],
    )
    description = models.TextField(
        blank=False,
        null=True,
        max_length=512,
        validators=[
            validators.MinLengthValidator(2),
            validators.MaxLengthValidator(512),
        ]
    )
    category = models.ForeignKey(
        Category,
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


    def clean(self) -> None:
        wallpapers = self.wallpapers.all()

        if not any(wallpapers):
            raise ValidationError(
                "Ensure that at least one wallpaper is uploaded.",
                code="wallpaper_required"
            )
        
        unique_dimensions = set()
        for wallpaper in wallpapers:
            if wallpaper.dimension is None or not isinstance(wallpaper.dimension, WallpaperDimension):
                raise ValidationError(
                    "Ensure that all wallpapers are related with a dimension.",
                    code="no_dimension"
                )
            dimension = wallpaper.dimension.width, wallpaper.dimension.height
            if dimension in unique_dimensions:
                raise ValidationError(
                    "Ensure that each wallpaper has unique dimension.",
                    code="duplicate_dimension"
                )
            unique_dimensions.add(dimension)


class Wallpaper(AbstractBaseModel):

    download_count = models.PositiveIntegerField(
        blank=False,
        null=False,
        default=0,
    )
    image = models.ImageField(
        verbose_name=SignalEffect.AUTO_DELETE_FILE + SignalEffect.AUTO_DELETE_OLD_FILE,
        blank=False,
        null=False,
        unique=True,
        upload_to=wallpaper_image_upload_path_generator,
        validators=[
            validate_image_max_file_size,
            ImageFormatAndFileExtensionsValidator((ImageFormat.JPEG, ))
        ],
    )
    thumbnail=models.ImageField(
        verbose_name=SignalEffect.AUTO_DELETE_FILE + SignalEffect.AUTO_DELETE_OLD_FILE,
        blank=False,
        null=False,
        unique=True,
        upload_to=wallpaper_thumbnail_upload_path_generator,
        validators=[
            MaxFileSizeValidator(20 * kb),
            ImageFormatAndFileExtensionsValidator((ImageFormat.WEBP, ))
        ],
    )
    dummy=models.ImageField(
        verbose_name=SignalEffect.AUTO_DELETE_FILE + SignalEffect.AUTO_DELETE_OLD_FILE,
        blank=False,
        null=False,
        unique=True,
        upload_to=wallpaper_dummy_upload_path_generator,
        validators=[
            MaxFileSizeValidator(100 * kb),
            ImageFormatAndFileExtensionsValidator((ImageFormat.WEBP, ))
        ],
    )
    dimension = models.ForeignKey(
        "WallpaperDimension",
        on_delete=models.SET_NULL,
        related_name='wallpapers',
        null=True,
    )
    wallpaper_group = models.ForeignKey(
        WallpaperGroup,
        on_delete=models.CASCADE,
        related_name='wallpapers',
    )

    objects: models.Manager["Wallpaper"] = models.Manager()


    def clean(self) -> None:
        self.image = cast(ImageFieldFile, self.image)
        self.thumbnail = cast(ImageFieldFile, self.thumbnail)
        self.dummy = cast(ImageFieldFile, self.dummy)
        image_file = cast(ImageFile, self.image.file)

        try:
            self.dimension = WallpaperDimension.objects.get(width=self.image.width, height=self.image.height)
        except WallpaperDimension.DoesNotExist:
            raise ValidationError(
                "Ensure the image dimensions match one of the allowed values, The current dimensions: %(width)s x %(height)s are not supported.",
                code="invalid_image_dimensions",
                params={"width": str(self.image.width), "height": str(self.image.height)}
            )
        
        thumbnail = generate_thumbnail_webp_from_jpeg(self.image, (512, 512))
        self.thumbnail.delete()
        self.thumbnail.save(wallpaper_thumbnail_upload_path_generator(self, 'thumbnail.webp'), ImageFile(thumbnail), save=False)

        dummy = generate_dummy_webp_from_jpeg(self.image)
        self.dummy.delete()
        self.dummy.save(wallpaper_dummy_upload_path_generator(self, 'dummy.webp'), ImageFile(dummy), save=False)


class WallpaperDimension(AbstractBaseModel):
    
    width = WallpaperDimensionField()
    height = WallpaperDimensionField()


    class Meta(AbstractBaseModel.Meta):
        constraints = [
            models.UniqueConstraint(fields=['width', 'height'], name="unique_width_height")
        ]

    wallpapers: RelatedManager["Wallpaper"]

    objects: models.Manager["WallpaperDimension"] = models.Manager()


    def delete_with_related_wallpapers(self) -> None:
        self.wallpapers.all().delete()
        self.delete()


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

    wallpaper_groups: RelatedManager[WallpaperGroup]

    objects: models.Manager["WallpaperTag"] = models.Manager()
