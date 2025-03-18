from typing import cast
from celery import chain, shared_task, group
from celery.result import GroupResult
from django.core.files.images import ImageFile
from app.models import Wallpaper, wallpaper_dummy_upload_path_generator
from common.image_utils import generate_webp_from_jpeg
from django.db.models.fields.files import ImageFieldFile
from zipfile import Path as ZipPath, ZipFile



# the patching idea was to provide zip file path and image file path in argument and work for now no storage no task persistance

@shared_task(bind=True, acks_late=False)
def save_wallpaper(self, image_path: str, zip_file_path: str) -> int: # type: ignore
    w = Wallpaper(image=ImageFile(ZipPath(raw_path).open('rb')))
    w.full_clean(exclude=('dimension', ))
    w.save()
    return w.id


@shared_task(ignore_result=True, acks_late=False)
def generate_and_save_dummy_wallpaper(wallpaper_id: int) -> None:
    w = Wallpaper.objects.get(pk=wallpaper_id)
    dummy_image_file = generate_webp_from_jpeg(w.image.file)
    dummy_image_field = cast(ImageFieldFile, w.dummy_image)
    dummy_image_field.save(wallpaper_dummy_upload_path_generator(w, 'dummy.webp'), dummy_image_file, save=True)


def bulk_upload(zip_file_path: str) -> str:
    with ZipFile(zip_file_path, 'r') as zip_file:
        group_result = cast(GroupResult, group(
            chain(save_wallpaper.s(file.relative_to(zip_file), zip_file_path), generate_and_save_dummy_wallpaper.s()) 
                for file in ZipPath(zip_file).glob('**/*.jpg')
        ).delay())
        group_result.save() # type: ignore[attr-defined]
        result_id = cast(str, group_result.id) # type: ignore[attr-defined]
        return result_id
