import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wallpaperzzz.settings')
django.setup()


from pathlib import Path
from adminapp.models import Category, SettingsStore
from django.core.files.images import ImageFile


category1 = Category(name="first category", thumbnail=ImageFile(Path('./fixture_files/Category1/thumbnail.png').open("rb")))
category2 = Category(name="first category", thumbnail=ImageFile(Path('./fixture_files/Category2/thumbnail.png').open("rb")))


settings = SettingsStore.settings.get()

