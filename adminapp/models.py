from pathlib import Path, PurePath
from typing import Self, cast, overload
from django.db import models
from django.core import validators
from django.conf import settings
from common.validators import MaxFileSizeValidator, ImageFormatAndFileExtensionsValidator
from common.utils import FileUploadPathGenerator, ImageFormat, get_file_extensions_for_image_format, compress_image_file, get_format_for_image_extension, generate_thumbnail
from common.regexes import name_regex_validator, key_regex_validator
from common.signals import SignalEffect
from common.models import AbstractBaseModel
from adminapp.fields import WallpaperDimensionField
from django.db.models.fields.files import ImageFieldFile
from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile


category_thumbnail_upload_path_generator = FileUploadPathGenerator(PurePath('category_thumbnails'), 'thumbnail')


wallpaper_group_thumbnail_upload_path_generator = FileUploadPathGenerator(PurePath('wallpaper_group_thumbnail'), 'thumbnail')


wallpaper_image_upload_path_generator = FileUploadPathGenerator(PurePath('wallpapers'), 'wallpaper')


def validate_image_max_file_size(value: ImageFieldFile) -> None:
    upper_limit = SettingsStore.settings.fetch_settings().maximum_image_file_size * 1024
    MaxFileSizeValidator(upper_limit)(value)
  

def validate_image_file_format_and_extension(value: ImageFieldFile) -> None:
    ImageFormatAndFileExtensionsValidator(SettingsStore.settings.fetch_allowed_image_file_formats())(value)


class _SettingsManager(models.Manager["SettingsStore"]):

    def fetch_settings(self: Self) -> "SettingsStore":
        return self.get_or_create(key='BASE_SETTINGS')[0]


    def fetch_allowed_image_file_formats(self) -> tuple[ImageFormat, ...]:
        settings = self.fetch_settings()
        allowed_image_file_formats: list[ImageFormat] = []

        for field in SettingsStore._meta.get_fields():
            if (isinstance(field, models.BooleanField)) and (field.db_column in ImageFormat) and (getattr(settings, field.name) is True):
                allowed_image_file_formats += [
                    ImageFormat[str(field.db_column)]
                ]
        
        return tuple(allowed_image_file_formats)
    

    def fetch_compress_image_setting(self) -> bool:
        return self.fetch_settings().compress_image_on_upload


class SettingsStore(AbstractBaseModel):
    
    key = models.CharField(
        primary_key=True,
        max_length=64,
        validators=[
            validators.MinLengthValidator(2),
            key_regex_validator,
        ],
        editable=False
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
        db_column=ImageFormat.PNG,
    )
    jpeg = models.BooleanField(
        blank=False,
        null=False,
        default=True,
        db_column=ImageFormat.JPEG,
    )
    webp = models.BooleanField(
        blank=False,
        null=False,
        default=True,
        db_column=ImageFormat.WEBP,
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
    thumbnail = models.ImageField(
        verbose_name=SignalEffect.AUTO_DELETE_FILE + SignalEffect.AUTO_DELETE_OLD_FILE,
        blank=False,
        null=False,
        unique=True,
        upload_to=category_thumbnail_upload_path_generator,
        validators=[
            MaxFileSizeValidator(settings.MAX_FILE_SIZE),
            ImageFormatAndFileExtensionsValidator((ImageFormat.PNG, ImageFormat.JPEG))
        ],
    )

    objects: models.Manager["Category"] = models.Manager()


class WallpaperGroup(AbstractBaseModel):

    description = models.TextField(
        blank=False,
        null=False,
        max_length=512,
        validators=[
            validators.MinLengthValidator(2),
            validators.MaxLengthValidator(512),
        ]
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='wallpaper_groups',
    )
    thumbnail = models.ImageField(
        verbose_name=SignalEffect.AUTO_DELETE_FILE + SignalEffect.AUTO_DELETE_OLD_FILE,
        blank=False,
        null=False,
        unique=True,
        upload_to=wallpaper_group_thumbnail_upload_path_generator,
        validators=[
            MaxFileSizeValidator(settings.MAX_FILE_SIZE),
            ImageFormatAndFileExtensionsValidator((ImageFormat.PNG, ImageFormat.JPEG, ImageFormat.WEBP))
        ],
        editable=False,
        default=ImageFile(Path('default.png').open('rb'))
    )

    wallpapers: models.Manager["Wallpaper"]

    objects: models.Manager["WallpaperGroup"] = models.Manager()


    def clean(self) -> None:
        first_wallpaper = self.wallpapers.first() 

        if first_wallpaper is None:
            raise ValidationError(
                "Ensure that at least one wallpaper is uploaded.",
                code="wallpaper_required"
            )


        self.thumbnail = cast(ImageFieldFile, self.thumbnail)

        if first_wallpaper.image.name is None or not isinstance(first_wallpaper.image.name, str):
            raise ValidationError(
                "Ensure that the wallpaper from which the thumbnail is generated is uploaded properly, it has no name.",
                code='no_image_name'
            )

        wallpaper_image_field_file = cast(ImageFieldFile, first_wallpaper.image)
        image_file = cast(ImageFile, wallpaper_image_field_file.file)
        with image_file.open('rb') as f:
            thumbnail_file = generate_thumbnail(f, (512, 512))
        self.thumbnail.save(wallpaper_group_thumbnail_upload_path_generator(self, first_wallpaper.image.name), ImageFile(thumbnail_file), save=False)


class Wallpaper(AbstractBaseModel):

    download_count = models.PositiveIntegerField(
        blank=False,
        null=False,
        default=0,
        editable=False,
    )
    compressed = models.BooleanField(
        blank=False,
        null=False,
        editable=False,
        default=SettingsStore.settings.fetch_compress_image_setting
    )
    image = models.ImageField(
        verbose_name=SignalEffect.AUTO_DELETE_FILE + SignalEffect.AUTO_DELETE_OLD_FILE,
        blank=False,
        null=False,
        unique=True,
        upload_to=wallpaper_image_upload_path_generator,
        validators=[
            validate_image_max_file_size,
            validate_image_file_format_and_extension
        ],
    )
    dimension = models.ForeignKey(
        "WallpaperDimension",
        on_delete=models.SET_NULL,
        related_name='wallpapers',
        editable=False,
        null=True
    )
    wallpaper_group = models.ForeignKey(
        WallpaperGroup,
        on_delete=models.CASCADE,
        related_name='wallpapers',
    )

    objects: models.Manager["Wallpaper"] = models.Manager()


    def clean(self) -> None:
        self.image = cast(ImageFieldFile, self.image)

        try:
            self.dimension = WallpaperDimension.objects.get(width=self.image.width, height=self.image.height)
        except WallpaperDimension.DoesNotExist:
            raise ValidationError(
                "Ensure the image dimensions match one of the allowed values, The current dimensions: %(width)s x %(height)s are not supported.",
                code="invalid_image_dimensions",
                params={"width": str(self.image.width), "height": str(self.image.height)}
            )
        
        if self.image.name is None:
            raise ValidationError(
                "Ensure that the image is uploaded properly, the image has no name.",
                code='no_image_name'
            )

        if SettingsStore.settings.fetch_compress_image_setting() is True:
            image_file = cast(ImageFile, self.image.file)
            with image_file.open('rb') as f:
                compressed_image_file = compress_image_file(f)
            self.image.save(wallpaper_image_upload_path_generator(self, self.image.name), ImageFile(compressed_image_file), save=False)
            self.compressed = True
        else:
            self.compressed = False


class WallpaperDimension(AbstractBaseModel):
    
    width = WallpaperDimensionField()
    height = WallpaperDimensionField()


    class Meta(AbstractBaseModel.Meta):
        constraints = [
            models.UniqueConstraint(fields=['width', 'height'], name="unique_width_height")
        ]

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
    wallpaper_group = models.ForeignKey(
        WallpaperGroup,
        on_delete=models.CASCADE,
        related_name='tags',
    )

    objects: models.Manager["WallpaperTag"] = models.Manager()
