# Generated by Django 5.1.6 on 2025-03-03 05:25

import adminapp.fields
import adminapp.models
import common.utils
import common.validators
import django.core.validators
import django.db.models.deletion
import django.db.models.manager
import pathlib
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True, validators=[django.core.validators.MinLengthValidator(2), django.core.validators.RegexValidator('^(?!.*\\s{2,})[A-Za-z]+(?: [A-Za-z]+)*$', 'Ensure that the name contains only English letters or spaces, with no leading or trailing spaces and no consecutive spaces.')])),
                ('thumbnail', models.ImageField(unique=True, upload_to=common.utils.FileUploadPathGenerator(pathlib.PurePosixPath('category_thumbnails'), 'thumbnail'), validators=[common.validators.MaxFileSizeValidator(1048576), common.validators.ImageTypeFileExtensionsValidator((common.utils.ImageType['PNG'], common.utils.ImageType['JPEG']))], verbose_name='auto_delete_fileauto_delete_old_file')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SettingsStore',
            fields=[
                ('key', models.CharField(max_length=64, primary_key=True, serialize=False, validators=[django.core.validators.MinLengthValidator(2), django.core.validators.RegexValidator('^[A-Z]+(?:_[A-Z]+)*$', 'Ensure that the key contains only uppercase English letters or underscores, with no leading or trailing underscores and no consecutive underscores.')])),
                ('maximum_image_file_size', models.PositiveIntegerField(default=1024, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10240)])),
                ('compress_image_on_upload', models.BooleanField(default=True)),
                ('png', models.BooleanField(db_column=common.utils.ImageType['PNG'], default=True)),
                ('jpeg', models.BooleanField(db_column=common.utils.ImageType['JPEG'], default=True)),
                ('webp', models.BooleanField(db_column=common.utils.ImageType['WEBP'], default=True)),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('settings', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='WallpaperDimension',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('width', adminapp.fields.WallpaperDimensionField()),
                ('height', adminapp.fields.WallpaperDimensionField()),
            ],
            options={
                'abstract': False,
                'constraints': [models.UniqueConstraint(fields=('width', 'height'), name='unique_width_height')],
            },
        ),
        migrations.CreateModel(
            name='WallpaperGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, validators=[django.core.validators.MinLengthValidator(2), django.core.validators.RegexValidator('^(?!.*\\s{2,})[A-Za-z]+(?: [A-Za-z]+)*$', 'Ensure that the name contains only English letters or spaces, with no leading or trailing spaces and no consecutive spaces.')])),
                ('thumbnail', models.ImageField(editable=False, unique=True, upload_to=common.utils.FileUploadPathGenerator(pathlib.PurePosixPath('wallpaper_group_thumbnail'), 'thumbnail'), validators=[common.validators.MaxFileSizeValidator(1048576), common.validators.ImageTypeFileExtensionsValidator((common.utils.ImageType['PNG'], common.utils.ImageType['JPEG']))], verbose_name='auto_delete_fileauto_delete_old_file')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wallpaper_groups', to='adminapp.category')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Wallpaper',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(unique=True, upload_to=common.utils.FileUploadPathGenerator(pathlib.PurePosixPath('wallpapers'), 'wallpaper'), validators=[adminapp.models.validate_image_max_file_size, adminapp.models.validate_image_file_extensions], verbose_name='auto_delete_fileauto_delete_old_file')),
                ('dimension', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='wallpapers', to='adminapp.wallpaperdimension')),
                ('wallpaper_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wallpapers', to='adminapp.wallpapergroup')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WallpaperTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=32, validators=[django.core.validators.MinLengthValidator(2), django.core.validators.RegexValidator('^(?!.*\\s{2,})[A-Za-z]+(?: [A-Za-z]+)*$', 'Ensure that the name contains only English letters or spaces, with no leading or trailing spaces and no consecutive spaces.')])),
                ('wallpaper_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='adminapp.wallpapergroup')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
