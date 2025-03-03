import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wallpaperzzz.settings')
django.setup()


from pathlib import Path
from adminapp.models import Category, SettingsStore, Wallpaper, WallpaperGroup
from django.core.files.images import ImageFile


category1 = Category(name="first category", thumbnail=ImageFile(Path('./fixture_files/Category1/thumbnail.png').open("rb")))
category2 = Category(name="first category", thumbnail=ImageFile(Path('./fixture_files/Category2/thumbnail.png').open("rb")))

settings = SettingsStore.settings.fetch_settings()

wpg = WallpaperGroup(
    name = 'world heritage',
    category = category1,
    thumbnail = ImageFile(
        Path('favorite.jpeg').open("rb"),
    ),
)

wallpaper = Wallpaper(
    image=ImageFile(
        Path('wallpaper.webp').open("rb")
    ),
    wallpaper_group = wpg,
)
