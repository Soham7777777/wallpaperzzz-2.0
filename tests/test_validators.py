import random
import unittest
from unittest.mock import Mock
from adminapp.validators import MaxFileSizeValidator
from django.db.models.fields.files import FieldFile
from django.core.exceptions import ValidationError


class TestMaxFileSizeValidator(unittest.TestCase):

    min_size, max_size = MaxFileSizeValidator._max_file_size_range
    valid_max_file_size = random.randint(min_size, max_size)
        

    def test_max_file_size_arg_range(self) -> None:
        MaxFileSizeValidator(max_file_size=self.valid_max_file_size)

        invalid_min_size = self.min_size - random.randint(1, 64)
        with self.assertRaises(ValueError) as err:
            MaxFileSizeValidator(max_file_size=invalid_min_size)
        self.assertEqual(err.exception.args[0], f"The max_file_size ({invalid_min_size}) must be an integer value within {self.min_size} to {self.max_size}.")

        invalid_max_size = self.max_size + random.randint(1, 64)
        with self.assertRaises(ValueError) as err:
            MaxFileSizeValidator(max_file_size=invalid_max_size)
        self.assertEqual(err.exception.args[0], f"The max_file_size ({invalid_max_size}) must be an integer value within {self.min_size} to {self.max_size}.")
    

    def test_validation(self) -> None:
        max_file_size = random.randint(self.min_size, self.max_size)
        validator_func = MaxFileSizeValidator(max_file_size=max_file_size)
        
        mock_field_file = Mock(spec_set=FieldFile)

        mock_field_file.size = max_file_size  
        validator_func(mock_field_file)

        mock_field_file.size = self.min_size  
        validator_func(mock_field_file)

        mock_field_file.size = self.max_size + random.randint(1, 64)
        with self.assertRaises(ValidationError) as err:
            validator_func(mock_field_file)
        self.assertEqual(err.exception.args[0], "Ensure that the file size is less than or equal to %(max_size)s bytes.")
        self.assertEqual(err.exception.code, 'file_too_large')
        self.assertEqual(err.exception.params, {'max_size': str(max_file_size)})
