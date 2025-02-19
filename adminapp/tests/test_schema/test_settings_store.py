from typing import cast
import unittest
from adminapp.models import SettingsStore
from django.db import models
from django.core import validators


class TestIsModel(unittest.TestCase):

    def test_is_model(self) -> None:
        self.assertTrue(issubclass(SettingsStore, models.Model))


class TestKeyField(unittest.TestCase):

    key_field = cast(models.CharField[str, str], SettingsStore._meta.get_field('key'))


    def test_is_char_field(self) -> None:
        self.assertIsInstance(self.key_field, models.CharField)


    def test_is_primary_key(self) -> None:
        self.assertTrue(self.key_field.primary_key)


    def test_string_length_constraints(self) -> None:
        self.assertEqual(self.key_field.max_length, 64)
        self.assertIn(validators.MinLengthValidator(2), self.key_field.validators)


    def test_has_regex(self) -> None:
        regex_pattern = r"^[A-Z]+(?:_[A-Z]+)*$"
        regex_invalid_message = "Ensure that the key contains only uppercase English letters or underscores, with no leading or trailing underscores and no consecutive underscores."
        self.assertIn(validators.RegexValidator(regex_pattern, regex_invalid_message), self.key_field.validators)
