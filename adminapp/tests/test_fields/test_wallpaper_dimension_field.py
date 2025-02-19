import unittest
from adminapp.fields import WallpaperDimensionField 
from django.db import models
from django.core import validators


class TestIsPositiveIntegerField(unittest.TestCase):

    def test_is_positive_integer_field(self) -> None:
        self.assertTrue(issubclass(WallpaperDimensionField, models.PositiveIntegerField))


class TestField(unittest.TestCase):

    field = WallpaperDimensionField()


    def test_required(self) -> None:
        self.assertTrue((not self.field.blank) and (not self.field.null))


    def test_min_max_validators(self) -> None:
        self.assertIn(validators.MinValueValidator(64), self.field.validators)
        self.assertIn(validators.MaxValueValidator(4096), self.field.validators)
