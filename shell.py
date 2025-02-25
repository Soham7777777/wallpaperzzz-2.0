import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wallpaperzzz.settings')
django.setup()


from pathlib import Path
from adminapp.models import Category
from django.core.files.images import ImageFile


c1 = Category(name="first category", thumbnail=ImageFile(Path('./fixture_files/Category1/thumbnail.png').open("rb")))
c2 = Category(name="first category", thumbnail=ImageFile(Path('./fixture_files/Category2/thumbnail.png').open("rb")))
