from pathlib import PurePath
import random
from typing import Callable
from django.test import SimpleTestCase
from unittest.mock import Mock, patch
from common.utils import FileUploadPathGenerator
import string
from django.db import models


class TestAttributeValidation(SimpleTestCase):

    valid_base_path = PurePath('some_relative_path')
    valid_name_prefix = 'A'*random.randint(*FileUploadPathGenerator._name_prefix_range)
    invalid_base_path = PurePath('/some_absolute_path')
    invalid_name_prefix_too_large = 'A'*(FileUploadPathGenerator._name_prefix_range[1] + random.randint(1, 64))
    invalid_name_prefix_too_small = 'A'*(FileUploadPathGenerator._name_prefix_range[0] - 1)
    invalid_name_prefix_contains_white_space = ('A'*(FileUploadPathGenerator._name_prefix_range[0])) + random.choice(string.whitespace) 


    def test_valid_attributes(self) -> None:
        FileUploadPathGenerator(self.valid_base_path, self.valid_name_prefix)
    
    
    def test_invalid_base_path(self) -> None:
        with self.assertRaisesMessage(ValueError, f"The base_path ({str(self.invalid_base_path)}) must be relative."):
            FileUploadPathGenerator(self.invalid_base_path, self.valid_name_prefix)

    
    def test_invalid_name_prefix_too_large(self) -> None:
        with self.assertRaisesMessage(ValueError, f"The name_prefix ({self.invalid_name_prefix_too_large}) must be within {FileUploadPathGenerator._name_prefix_range[0]} to {FileUploadPathGenerator._name_prefix_range[1]} characters."):
            FileUploadPathGenerator(self.valid_base_path, self.invalid_name_prefix_too_large)


    def test_invalid_name_prefix_too_small(self) -> None:
        with self.assertRaisesMessage(ValueError, f"The name_prefix ({self.invalid_name_prefix_too_small}) must be within {FileUploadPathGenerator._name_prefix_range[0]} to {FileUploadPathGenerator._name_prefix_range[1]} characters."):
            FileUploadPathGenerator(self.valid_base_path, self.invalid_name_prefix_too_small)
    

    def test_invalid_name_prefix_contains_white_space(self) -> None:
        with self.assertRaisesMessage(ValueError, f"The name_prefix ({self.invalid_name_prefix_contains_white_space}) must not contain any whitespace characters."):
            FileUploadPathGenerator(self.valid_base_path, self.invalid_name_prefix_contains_white_space)

    
class TestFunction(SimpleTestCase):

    base_path = PurePath('some_relative_path')
    name_prefix = 'A'*random.randint(*FileUploadPathGenerator._name_prefix_range)
    file_name_from_user = 'someimage.png'
    mock_instance = Mock(spec_set=models.Model)
    function = FileUploadPathGenerator(base_path, name_prefix)


    @patch("common.utils.time.time", return_value=1739850041.4739854)
    def test_function(self, mock_timestamp: Callable[[], float]) -> None:
        filepath = self.function(self.mock_instance, self.file_name_from_user)
        self.assertEqual(filepath, str(self.base_path / f"{self.name_prefix}{''.join(str(mock_timestamp()).split('.'))}{PurePath(self.file_name_from_user).suffix}"))
