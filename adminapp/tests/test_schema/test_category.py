from typing import cast
import unittest
from django.db import models
from adminapp.models import Category
from django.core import validators


class TestIsModel(unittest.TestCase):

    def test_is_model(self) -> None:
        self.assertTrue(issubclass(Category, models.Model))


class TestNameField(unittest.TestCase):
    
    name_field = cast(models.CharField[str, str], Category._meta.get_field('name'))
    

    def test_is_char_field(self) -> None:
        self.assertIsInstance(self.name_field, models.CharField)
    

    def test_required(self) -> None:
        self.assertTrue(not self.name_field.blank and not self.name_field.null)
    

    def test_uniqueness(self) -> None:
        self.assertTrue(self.name_field.unique)


    def test_string_length_constraints(self) -> None:
        self.assertEqual(self.name_field.max_length, 32)
        self.assertIn(validators.MinLengthValidator(2), self.name_field.validators)


    def test_has_regex(self) -> None:
        regex_pattern = r"^(?!.*\s{2,})[A-Za-z]+(?: [A-Za-z]+)*$"
        regex_invalid_message = "The name can only contain English latters or spaces, with no leading or trailing spaces and no consecutive spaces."
        self.assertIn(validators.RegexValidator(regex_pattern, regex_invalid_message), self.name_field.validators)
