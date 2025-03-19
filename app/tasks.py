from pathlib import Path
from typing import cast
from celery import chain, shared_task, group
from celery.result import GroupResult
from django.core.files.images import ImageFile
from app.models import Wallpaper, wallpaper_dummy_upload_path_generator
from common.image_utils import generate_webp_from_jpeg
from django.db.models.fields.files import ImageFieldFile
from zipfile import Path as ZipPath
from celery.exceptions import Reject


terminal_status = ('SUCCESS', 'FAILURE')

@shared_task(acks_late=False)
def save_wallpaper(image_path: str, zip_file_path: str) -> int: # type: ignore
    w = Wallpaper(image=ImageFile(ZipPath(zip_file_path, at=image_path).open('rb')))
    w.full_clean(exclude=('dimension', ))
    w.save()
    return w.id


@shared_task(acks_late=False)
def generate_and_save_dummy_wallpaper(wallpaper_id: int) -> None:
    w = Wallpaper.objects.get(pk=wallpaper_id)

    if w.dummy_image != '':
        raise Reject("Dummy already exists", requeue=False)
    
    dummy_image_file = generate_webp_from_jpeg(w.image.file)
    dummy_image_field = cast(ImageFieldFile, w.dummy_image)
    dummy_image_field.save(wallpaper_dummy_upload_path_generator(w, 'dummy.webp'), dummy_image_file, save=True)


def bulk_upload(zip_file_path: Path) -> str:
    group_result = cast(GroupResult, group(
        chain(save_wallpaper.s(file.at, str(file.root.filename)), generate_and_save_dummy_wallpaper.s()) 
            for file in ZipPath(zip_file_path).glob('**/*.jpg')
    ).delay())
    group_result.save() # type: ignore[attr-defined]
    result_id = cast(str, group_result.id) # type: ignore[attr-defined]
    return result_id


def calculate_status_percentage(result_id: str) -> int:
    group_result = cast(GroupResult, GroupResult.restore(result_id)) # type: ignore[attr-defined]
    total_results = len(group_result) * 2 # type: ignore[arg-type]
    ready_results = 0

    for result in group_result: # type: ignore[attr-defined]
        if result.status in terminal_status: ready_results += 1
        if result.parent.status in terminal_status: ready_results += 1

    return (ready_results * 100)//total_results
