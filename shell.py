import preshell
from pathlib import Path
from adminapp.models import Category, SettingsStore, Wallpaper, WallpaperGroup, WallpaperDimension
from django.core.files.images import ImageFile
from common.image_utils import ImageFormat
from PIL import Image

category1 = Category(name="first category", thumbnail=ImageFile(Path('nails-category.jpg').open("rb")))

settings = SettingsStore.settings.fetch_settings()
wpg = WallpaperGroup()
wd = WallpaperDimension(width=2848, height=1899)

wallpaper = Wallpaper(
    image = ImageFile(
        Path("nails-wallpaper.jpg").open('rb')
    ),
    dimension = wd,
    wallpaper_group = wpg
)

category1.save()
wpg.save()
wd.save()

x = 1
x = 'str'
