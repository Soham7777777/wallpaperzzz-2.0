import uuid
from typing import cast
from celery import shared_task, Task
from django.core.files.images import ImageFile
from common.image_utils import generate_webp_from_jpeg
from django.db.models.fields.files import ImageFieldFile
from zipfile import Path as ZipPath
from celery.exceptions import Reject
from django.core.exceptions import ValidationError
from celery.exceptions import Reject


@shared_task(bind=True, ignore_result=False, acks_late=False)
def save_wallpaper(self: Task[[str, str], str], image_path: str, zip_file_path: str) -> str:
    from app.models import BulkUploadProcess, Wallpaper, BulkUploadProcessError

    w = Wallpaper(image=ImageFile(ZipPath(zip_file_path, at=image_path).open('rb')))

    try:
        w.full_clean(exclude=('dimension', ))
    except ValidationError as err:
        group_id = cast(str, self.request.chain[0]['options']['group_id']) # type: ignore
        
        if group_id is not None:
            try:
                process = BulkUploadProcess.objects.get(pk=uuid.UUID(group_id))
                BulkUploadProcessError.objects.create(
                    process=process,
                    validation_error=' '.join(err.messages),
                    at_file=image_path
                )
            except BulkUploadProcess.DoesNotExist:
                ...
                
        raise err

    w.save()
    return w.uuid.hex


@shared_task(bind=True, ignore_result=False, acks_late=False)
def generate_and_save_dummy_wallpaper(self: Task[[str], None], wallpaper_id: str) -> None:
    from app.models import Wallpaper, wallpaper_dummy_upload_path_generator

    w = Wallpaper.objects.get(pk=uuid.UUID(wallpaper_id))

    if w.dummy_image != '':
        raise Reject("Dummy already exists", requeue=False)
    
    dummy_image_file = generate_webp_from_jpeg(w.image.file)
    dummy_image_field = cast(ImageFieldFile, w.dummy_image)
    dummy_image_field.save(wallpaper_dummy_upload_path_generator(w, 'dummy.webp'), dummy_image_file, save=True)
