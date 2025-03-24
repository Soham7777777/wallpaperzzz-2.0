from typing import cast
from django import forms
from project.settings import mb
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.core.exceptions import ValidationError
from pathlib import PurePath
import zipfile


class BulkUploadForm(forms.Form):
    zip_file = forms.FileField(
        label='Wallpapers Zip',
        required=True,
        max_length=64,
        allow_empty_file=False,
        help_text=f"Upload a zip file containing wallpapers that does not exceed {settings.MAX_BULK_UPLOAD_SIZE // mb} MB."
    )

    def clean_zip_file(self) -> zipfile.ZipFile:
        uploaded_file = cast(UploadedFile, self.cleaned_data['zip_file'])

        if uploaded_file.name is None or PurePath(uploaded_file.name).suffix != '.zip':
            raise ValidationError(
                "Only '.zip' extension is allowed.",
                code='invalid_zip_file_extension'
            )

        if uploaded_file.file is None:
            raise ValidationError(
                "zip file is required.",
                code='zip_file_required'
            )

        try:
            zip_file = zipfile.ZipFile(uploaded_file)
        except zipfile.BadZipfile as err:
            raise ValidationError(
                'Invalid zip file.',
                code='invalid_zip_file'
            )
        
        if (bad_file:=zip_file.testzip()) is not None:
            raise ValidationError(
                "Bad file found in zip: %(bad_file)s",
                code='bad_file_found_in_zip_file',
                params=dict(bad_file=bad_file)
            )

        return zip_file
