import os
import time
from typing import cast
import django
import django_stubs_ext


django_stubs_ext.monkeypatch()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

# ================================================================
# ================================================================
# ================================================================
# ================================================================
# ================================================================


from django.db import connection
from django.conf import settings
from app.tasks import save_wallpaper, generate_and_save_dummy_wallpaper
from pathlib import Path
from app.models import Category, SettingsStore, Wallpaper, WallpaperGroup, WallpaperDimension
from django.core.files.images import ImageFile
from common.image_utils import ImageFormat
from PIL import Image
from celery import group, chain
from celery.result import AsyncResult, GroupResult


y = 1
y = 'str'


# p = Path('category.jpg')
# category1 = Category(name="first category", description="some day", thumbnail=ImageFile(Path('category.jpg').open("rb")))
# category2 = Category(name='second_category', description="other day", thumbnail=ImageFile(Path('./wallpapers/pexels-137666-710743.jpg').open("rb")))
# settings = SettingsStore.settings.fetch_settings()


# dimensions = {(3669, 2446), (5760, 3840), (2303, 3012), (3648, 2432), (2766, 3795), (8006, 5504), (3550, 4734), (6851, 4139), (3318, 4976), (3951, 5926), (3272, 4908), (8000, 6000), (2500, 1667), (5617, 3744), (4376, 2917), (4912, 7360), (2741, 4109), (4560, 3040), (7360, 4912), (3694, 3087), (2563, 3840), (5184, 3456), (3888, 2592), (4806, 3199), (3648, 5472), (5777, 3851), (5520, 4000), (8192, 5461), (3275, 2465), (2048, 1295), (3968, 2645), (4000, 5176), (4256, 2832), (3744, 5616), (3423, 4279), (2000, 1123), (6720, 4480), (4169, 7412), (5748, 4000), (5464, 3640), (4000, 3000), (2000, 1333), (5647, 3752), (6332, 4221), (5655, 3775), (6016, 4000), (4001, 6000), (4752, 3168), (2848, 1899), (3936, 2624), (2309, 3464), (5461, 8192), (4126, 2751), (5360, 3560), (4480, 6720), (4852, 7275), (5388, 3777), (5760, 3240), (5032, 7544), (3200, 2560), (7728, 4347), (4388, 6582), (5700, 3601), (3361, 4201), (2772, 1890), (3793, 2845), (2888, 3306), (5616, 3744), (3840, 5760), (6144, 8192), (2606, 3648), (6240, 4160), (3636, 2583), (3511, 5267), (4803, 3202), (2000, 1086), (3003, 4504), (4925, 3328), (3640, 5460), (4640, 6960), (2899, 4348), (4272, 2848), (1898, 1266), (2326, 3495), (2999, 3999), (4472, 7952), (2500, 1682), (4000, 6016), (1775, 3157), (4480, 5451), (4000, 3200), (5472, 3072), (5325, 3575), (5135, 3423), (5000, 8000), (5472, 3648), (4000, 6000), (4501, 3005), (2500, 1794), (4368, 2457), (2848, 3560), (2048, 1365), (4672, 7008), (5439, 3626), (4500, 8000), (4169, 6332), (2731, 4097), (4160, 6240), (4593, 3062), (3456, 5184), (7680, 4320), (4896, 3264), (6209, 3665), (7008, 4672), (5304, 7952), (4824, 7232), (6000, 4000), (7941, 5297), (4896, 3010), (3848, 2565), (4928, 3280), (6070, 3414), (2133, 3200), (2496, 3624), (3510, 5260), (1667, 2500), (3500, 2333), (4928, 3264), (8000, 5333)}

# for dimension in dimensions:
#     WallpaperDimension.objects.create(width=dimension[0], height=dimension[1])


# wd = WallpaperDimension(width=8192, height=5461)

# wallpaper1 = Wallpaper(
#     image = ImageFile(
#         Path("/home/soham/Playgrounds/raster_playground/raster_data/wallpapers/pexels-137666-710743.jpg").open('rb')
#     ),
# )

# wallpaper2 = Wallpaper(
#     image = ImageFile(
#         Path("wallpaper.jpg").open('rb')
#     ),
# )

# category1.save()
# wd.save()

# p = settings.BASE_DIR / 'wallpapers'
# group_result = cast(GroupResult, group(
#     chain(save_wallpaper.s(str(x)), generate_and_save_dummy_wallpaper.s())
#         for x in p.glob('*')
# ).delay())
# group_result.save()
# print(group_result.id)
# print(GroupResult.restore(group_result.id))

# import zipfile

# wallpaper_zip_path = settings.MEDIA_ROOT / 'wallpapers.zip'

# with zipfile.ZipFile(wallpaper_zip_path, 'r') as zip_file:
# zip_file = zipfile.ZipFile(wallpaper_zip_path, 'r')

from app.models import BulkUploadProcess
import zipfile
process = BulkUploadProcess.upload_procedures.bulk_upload(zipfile.Path(settings.BASE_DIR / 'temp/wallpapers.zip'))

while True:
    print(process.calculate_progress())
    time.sleep(1)
