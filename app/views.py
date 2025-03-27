import json
from typing import cast
import uuid
from django.conf import settings
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import render, redirect, resolve_url, get_object_or_404
from app.forms import ZipFileStoreModelForm, ProgressForm
from app.models import BulkUploadProcess, Wallpaper
import zipfile


def index(request: HttpRequest) -> HttpResponse:
    return redirect(resolve_url('bulk_upload'))


def bulk_upload(request: HttpRequest) -> HttpResponse:

    if request.method == 'POST':
        form = ZipFileStoreModelForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            try:
                BulkUploadProcess.upload_procedures.bulk_upload(zipfile.Path(form.instance.get_zip_file()))
            except ValueError:
                ...
            response = HttpResponse()
            response['HX-Refresh'] = 'true'
            return response
        else:
            return render(request, 'app/partials/form_errors.html', dict(form=form))

    return render(request, 'app/bulk_upload.html', dict(form=ZipFileStoreModelForm(), processes=BulkUploadProcess.objects.all()))


def progress(request: HttpRequest) -> HttpResponse:
    form = ProgressForm(request.GET)
    if form.is_valid():
        process_uuid = form.cleaned_data['process_uuid']

        try:
            process = get_object_or_404(BulkUploadProcess, pk=uuid.UUID(process_uuid))
            progress = process.calculate_progress()
            width = progress.calculate_percentage()
        except ValueError:
            return HttpResponse(286)
        
        errors = [f"<b>{error.at_file}</b>: {error.validation_error}" for error in  process.errors.all()]

        if progress.finished_tasks == progress.total_tasks:
            response = HttpResponse(status=286)
        else:        
            response = HttpResponse()
            
        response['HX-Trigger-After-Swap'] = json.dumps({f'update_{process_uuid}': {'width': width, 'errors': errors}})

        return response
    
    return HttpResponse(286)
    

def wallpapers(request: HttpRequest) -> HttpResponse:
    images = Wallpaper.objects.exclude(dummy_image__isnull=True).values('dummy_image')[:10]
    return render(request, 'app/wallpapers.html', dict(images=images, media_url=settings.MEDIA_URL))
