from django.urls import path
from app import views


urlpatterns = [

    path('', views.index),
    path('bulk-upload', views.bulk_upload, name='bulk_upload'),
    path('progress', views.progress, name='progress'),
    path('wallpapers', views.wallpapers, name='wallpapers'),

]
