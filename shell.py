import preshell
from pathlib import Path
from adminapp.models import Category, SettingsStore, Wallpaper, WallpaperGroup, WallpaperDimension
from django.core.files.images import ImageFile
from common.image_utils import ImageFormat
from PIL import Image

category1 = Category(name="first category", thumbnail=ImageFile(Path('category.jpg').open("rb")))
settings = SettingsStore.settings.fetch_settings()

wpg = WallpaperGroup()

wd = WallpaperDimension(width=8192, height=5462)

wallpaper1 = Wallpaper(
    image = ImageFile(
        Path("wallpaper.jpg").open('rb')
    ),
    dimension = wd,
    wallpaper_group = wpg
)

wallpaper2 = Wallpaper(
    image = ImageFile(
        Path("wallpaper.jpg").open('rb')
    ),
    dimension = wd,
    wallpaper_group = wpg
)

# category1.save()
# wd.save()
# wpg.save()

x = 1
x = 'str'
