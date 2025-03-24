from typing import cast
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from app.forms import BulkUploadForm
import zipfile


def bulk_upload(request: HttpRequest) -> HttpResponse:

    if request.method == 'POST':

        form = BulkUploadForm(request.POST, request.FILES)

        if form.is_valid():
            zip_file = cast(zipfile.ZipFile, form.cleaned_data['zip_file'])
        else:
            return render(request, 'app/bulk_upload.html', dict(form=form))

    return render(request, 'app/bulk_upload.html', dict(form=BulkUploadForm()))
