from dataclasses import dataclass
from pathlib import PurePath
from typing import cast
import uuid
import zipfile
from django.db import models
from django.core import validators
from django.conf import settings
from common.validators import MaxFileSizeValidator, ImageFormatAndFileExtensionsValidator
from common.unique_file_path_generators import UniqueFilePathGenerator
from common.image_utils import ImageFormat, get_file_extensions_for_image_format
from common.regexes import name_regex_validator, key_regex_validator
from common.signals import SignalEffect
from common.models import AbstractBaseModel
from app.fields import WallpaperDimensionField
from django.db.models.fields.files import ImageFieldFile, FieldFile
from django.core.exceptions import ValidationError
from django_stubs_ext.db.models.manager import RelatedManager
from project.settings import kb
from celery.result import GroupResult
from zipfile import Path as ZipPath
from celery import group, chain
from app.tasks import save_wallpaper, generate_and_save_dummy_wallpaper
from project.settings import mb


category_thumbnail_upload_path_generator = UniqueFilePathGenerator(PurePath('category_thumbnails'), 'thumbnail')

wallpaper_image_upload_path_generator = UniqueFilePathGenerator(PurePath('wallpapers'), 'wallpaper')

wallpaper_dummy_upload_path_generator = UniqueFilePathGenerator(PurePath('wallpapers'), 'dummy')

zip_file_store_upload_path_generator = UniqueFilePathGenerator(PurePath('zip_files'), 'zip')


def validate_image_max_file_size(value: ImageFieldFile) -> None:
    upper_limit = SettingsStore.settings.fetch_maximum_image_file_size_in_kb()
    MaxFileSizeValidator(upper_limit)(value)


def validate_group_process_exists(value: uuid.UUID) -> None:
    if GroupResult.restore(str(value)) is None: # type: ignore[attr-defined]
        raise ValidationError(
            "The group process %(process_uuid)s does not exists.",
            code='group_process_does_not_exists',
            params={'process_uuid': str(value)}
        )


@dataclass
class Progress:
    finished_tasks: int
    total_tasks: int

    def calculate_percentage(self) -> int:
        try:
            return (self.finished_tasks * 100) // self.total_tasks
        except ZeroDivisionError:
            return 0


class _SettingsManager(models.Manager["SettingsStore"]):

    def fetch_settings(self) -> "SettingsStore":
        return self.get_or_create(key='BASE_SETTINGS')[0]
    

    def fetch_maximum_image_file_size_in_kb(self) -> int:
        return self.fetch_settings().maximum_image_file_size * 1024


class _BulkUploadManager(models.Manager["BulkUploadProcess"]):

    def bulk_upload(self, zip_file_path: ZipPath) -> "BulkUploadProcess":
        paths = []
        extensions = get_file_extensions_for_image_format(ImageFormat.JPEG)
        glob_patterns = [f'**/*{extension}' for extension in extensions]
        glob_patterns += [f'*{extension}' for extension in extensions]

        for glob_pattern in glob_patterns: paths += [*zip_file_path.glob(glob_pattern)]
        
        if not any(paths):
            raise ValueError('No files to process.')

        group_result = cast(GroupResult, group(
                chain(

                    save_wallpaper.s(file.at, str(file.root.filename)),
                    
                    generate_and_save_dummy_wallpaper.s(),

                ) 
                for file in paths
            )(countdown=10)
        )
        group_result.save() # type: ignore[attr-defined]
        result_id = cast(str, group_result.id) # type: ignore[attr-defined]
        return BulkUploadProcess.objects.create(uuid=uuid.UUID(result_id))


class SettingsStore(AbstractBaseModel):
    
    uuid = None # type: ignore[assignment]

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


class BulkUploadProcess(AbstractBaseModel):

    terminal_status = ('SUCCESS', 'FAILURE')
    uuid = models.UUIDField(
        primary_key=True,
        validators=[
            validate_group_process_exists,
        ]
    )
    started_at = models.DateTimeField(auto_now=True)
    errors: RelatedManager["BulkUploadProcessError"]

    objects: models.Manager["BulkUploadProcess"] = models.Manager()
    upload_procedures: _BulkUploadManager = _BulkUploadManager()


    def calculate_progress(self) -> Progress:
        group_result = cast(GroupResult | None, GroupResult.restore(str(self.uuid))) # type: ignore[attr-defined]

        if group_result is None:
            raise ValueError(f'The group process for id {str(self.uuid)} cannot be found.')

        total_results = len(group_result) * 2 # type: ignore[arg-type]
        ready_results = 0

        for result in group_result: # type: ignore[attr-defined]
            if result.status in BulkUploadProcess.terminal_status: ready_results += 1
            if result.parent.status in BulkUploadProcess.terminal_status: ready_results += 1

        return Progress(ready_results, total_results)


class BulkUploadProcessError(AbstractBaseModel):

    process = models.ForeignKey(
        BulkUploadProcess,
        on_delete=models.CASCADE,
        related_name='errors',
    )
    validation_error = models.CharField(
        max_length=64,
        validators=[
            validators.MinLengthValidator(2),
        ]
    )
    at_file = models.CharField(
        max_length=1024,
        validators=[
            validators.MinLengthValidator(1),
        ]
    )

    objects: models.Manager["BulkUploadProcessError"] = models.Manager()


class ZipFileStore(AbstractBaseModel):

    zip_file = models.FileField(
        verbose_name=SignalEffect.AUTO_DELETE_FILE + SignalEffect.AUTO_DELETE_OLD_FILE,
        upload_to=zip_file_store_upload_path_generator,
        unique=True,
        help_text=f"Upload a zip file containing wallpapers that does not exceed {settings.MAX_BULK_UPLOAD_SIZE // mb} MB.",
        validators=[
            validators.FileExtensionValidator(('zip', )),
            MaxFileSizeValidator(500 * mb),
        ],
        max_length=64
    )


    def clean(self) -> None:
        zip_file = cast(FieldFile, self.zip_file)

        try:
            zipfile.ZipFile(zip_file)
        except zipfile.BadZipfile as err:
            raise ValidationError(
                'Invalid zip file.',
                code='invalid_zip_file'
            )
        
        if (bad_file:=zipfile.ZipFile(zip_file).testzip()) is not None:
            raise ValidationError(
                "Bad file found in zip: %(bad_file)s",
                code='bad_file_found_in_zip_file',
                params=dict(bad_file=bad_file)
            )

        # needs more validation to prevent attacks like zip bomb


    def get_zip_file(self) -> zipfile.ZipFile:
        zip_file = cast(FieldFile, self.zip_file)
        return zipfile.ZipFile(zip_file)
