import preshell
from pathlib import Path
from adminapp.models import Category, SettingsStore, Wallpaper, WallpaperGroup, WallpaperDimension
from django.core.files.images import ImageFile
from common.utils import compress_image_file, ImageFormat
from PIL import Image


category1 = Category(name="first category", thumbnail=ImageFile(Path('./fixture_files/Category1/thumbnail.png').open("rb")))
category2 = Category(name="first category", thumbnail=ImageFile(Path('./fixture_files/Category2/thumbnail.png').open("rb")))

settings = SettingsStore.settings.fetch_settings()

wpg = WallpaperGroup(
    description = 'world heritage',
    category = category1,
)

WallpaperGroup()

wd = WallpaperDimension(width=550, height=368)

wallpaper = Wallpaper(
    image = ImageFile(
        Path("./fixture_files/stock_photos/landscape.webp").open('rb')
    ),
    wallpaper_group = wpg,
    dimension = wd
)

# original_png = ImageFile(Path('./fixture_files/Category3/thumbnail.png').open("rb"))
# original_jpeg = ImageFile(Path('./fixture_files/stock_photos/woman-with-flowers.jpg').open("rb"))
# original_webp = ImageFile(Path('./fixture_files/stock_photos/landscape.webp').open("rb"))

# compressed_png = compress_image_file(original_png, ImageFormat.PNG)
# compressed_jpeg = compress_image_file(original_jpeg, ImageFormat.JPEG)
# compressed_webp = compress_image_file(original_webp, ImageFormat.WEBP)


category1.save()
wd.save()
