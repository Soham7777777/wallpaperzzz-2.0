from pathlib import Path
from typing import cast
from celery import shared_task
from django.core.files.images import ImageFile
from app.models import Wallpaper, wallpaper_dummy_upload_path_generator
from django.conf import settings
from common.image_utils import generate_webp_from_jpeg
from django.db.models.fields.files import ImageFieldFile


@shared_task
def save_wallpaper(raw_path: str) -> int:
    w = Wallpaper(image=ImageFile(Path(raw_path).relative_to(settings.BASE_DIR).open('rb')))
    w.full_clean(exclude=('dimension', ))
    w.save()
    return w.id


@shared_task(ignore_result=True)
def generate_and_save_dummy_wallpaper(wallpaper_id: int) -> None:
    w = Wallpaper.objects.get(pk=wallpaper_id)
    dummy_image_file = generate_webp_from_jpeg(w.image.file)
    dummy_image_field = cast(ImageFieldFile, w.dummy_image)
    dummy_image_field.save(wallpaper_dummy_upload_path_generator(w, 'dummy.webp'), dummy_image_file, save=True)


def bulk_upload(path_to_zipfile: Path) -> None:
    # unzip to tempdir
    # create a "progress" data structure to redis or django cache: Some kind of data store that temporarely allows read-write access in thread safe manner so that multiple celery task process can update the task progress 
    # loop files in tempdir and run task for each file: we need to store data about which files are done to make tasks idempotent
        # the task will update the progress datastructure and we can poll that in other function
        # the task will also report the file-names with error message which are faild to compress
    pass
