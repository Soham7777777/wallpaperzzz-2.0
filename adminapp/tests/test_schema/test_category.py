from pathlib import PurePath
from typing import cast
import unittest
from unittest.mock import patch
from django.conf import settings
from django.db import models
from adminapp.models import Category
from adminapp.validators import MaxFileSizeValidator
from django.core import validators
from adminapp.utils import FileUploadPathGenerator


class TestIsModel(unittest.TestCase):

    def test_is_model(self) -> None:
        self.assertTrue(issubclass(Category, models.Model))


class TestNameField(unittest.TestCase):
    
    name_field = cast(models.CharField[str, str], Category._meta.get_field('name'))
    

    def test_is_char_field(self) -> None:
        self.assertIsInstance(self.name_field, models.CharField)
    

    def test_required(self) -> None:
        self.assertTrue((not self.name_field.blank) and (not self.name_field.null))
    

    def test_uniqueness(self) -> None:
        self.assertTrue(self.name_field.unique)


    def test_string_length_constraints(self) -> None:
        self.assertEqual(self.name_field.max_length, 32)
        self.assertIn(validators.MinLengthValidator(2), self.name_field.validators)


    def test_has_regex(self) -> None:
        regex_pattern = r"^(?!.*\s{2,})[A-Za-z]+(?: [A-Za-z]+)*$"
        regex_invalid_message = "Ensure that the name contains only English letters or spaces, with no leading or trailing spaces and no consecutive spaces."
        self.assertIn(validators.RegexValidator(regex_pattern, regex_invalid_message), self.name_field.validators)


class TestThumbnailField(unittest.TestCase):

    thumbnail_field = cast(models.ImageField, Category._meta.get_field('thumbnail'))


    def test_is_image_field(self) -> None:
        self.assertIsInstance(self.thumbnail_field, models.ImageField)


    def test_required(self) -> None:
        self.assertTrue((not self.thumbnail_field.blank) and (not self.thumbnail_field.null))
    

    def test_uniqueness(self) -> None:
        self.assertTrue(self.thumbnail_field.unique)


    def test_has_extension_validator(self) -> None:
        self.assertIn(validators.FileExtensionValidator(('png', )),  self.thumbnail_field.validators)


    def test_has_max_file_size_validator(self) -> None:
        self.assertIn(MaxFileSizeValidator(max_file_size=settings.MAX_FILE_SIZE), self.thumbnail_field.validators)


    def test_has_upload_to_callable(self) -> None:
        self.assertEqual(self.thumbnail_field.upload_to, FileUploadPathGenerator(base_path=PurePath('category_thumbnails'), name_prefix='thumbnail'))



# filename = 'somefile.png'
# with patch('time.time') as mock_time_stamp:
#     mock_time_stamp.return_value = 1739624091.3249042
#     upload_path = PurePath(get_upload_path(Mock(), 'somefile.png'))
#     self.assertEqual(str(upload_path.parent), 'category_thumbnail')
#     self.assertEqual(upload_path.name, f'thumbnail{''.join(str(time.time()).split('.'))}{PurePath(filename).suffix}')