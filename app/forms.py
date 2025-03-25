from django import forms
from app.models import ZipFileStore


class ZipFileStoreModelForm(forms.ModelForm[ZipFileStore]):
    template_name = 'app/forms/bulk_upload_form.html'

    class Meta:
        model = ZipFileStore
        fields = ['zip_file', ]


class ProgressForm(forms.Form):
    process_uuid = forms.CharField(
        required=True,
    )
