from django.urls import path
from app.views import bulk_upload


urlpatterns = [

    path('bulk_upload', bulk_upload),

]
