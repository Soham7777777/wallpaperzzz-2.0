from typing import cast
import unittest
from django.db import models
from adminapp.models import WallpaperDimension
from adminapp.fields import WallpaperDimensionField


class TestIsModel(unittest.TestCase):

    def test_is_model(self) -> None:
        self.assertTrue(issubclass(WallpaperDimension, models.Model))


class TestWidthField(unittest.TestCase):

    width_field = cast(models.PositiveIntegerField[int, int], WallpaperDimension._meta.get_field('width'))


    def test_is_wallpaper_dimension_field(self) -> None:
        self.assertIsInstance(self.width_field, WallpaperDimensionField)


class TestHeightField(unittest.TestCase):

    height_field = cast(models.PositiveIntegerField[int, int], WallpaperDimension._meta.get_field('height'))


    def test_is_wallpaper_dimension_field(self) -> None:
        self.assertIsInstance(self.height_field, WallpaperDimensionField)    


class TestConstraints(unittest.TestCase):

    def test_unique_constraint(self) -> None:
        self.assertIn(models.UniqueConstraint(fields=['width', 'height'], name='unique_width_height'), WallpaperDimension._meta.constraints)
