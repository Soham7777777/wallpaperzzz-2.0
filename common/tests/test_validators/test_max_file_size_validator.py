import random
from django.test import SimpleTestCase
from unittest.mock import Mock
from common.validators import MaxFileSizeValidator
from django.db.models.fields.files import FieldFile
from django.core.exceptions import ValidationError


class TestMaxFileSizeAttributeRange(SimpleTestCase):

    min_size, max_size = MaxFileSizeValidator._max_file_size_range
    valid_max_file_size = random.randint(min_size, max_size)
        

    def test_valid_range(self) -> None:
        MaxFileSizeValidator(self.valid_max_file_size)


    def test_invalid_min_size(self) -> None:
        invalid_min_size = self.min_size - random.randint(1, 64)
        with self.assertRaisesMessage(ValueError, f"The max_file_size ({invalid_min_size}) must be an integer value within {self.min_size} to {self.max_size}."):
            MaxFileSizeValidator(invalid_min_size)


    def test_invalid_max_size(self) -> None:
        invalid_max_size = self.max_size + random.randint(1, 64)
        with self.assertRaisesMessage(ValueError, f"The max_file_size ({invalid_max_size}) must be an integer value within {self.min_size} to {self.max_size}."):
            MaxFileSizeValidator(invalid_max_size)
    

class TestValidation(SimpleTestCase):

    function = MaxFileSizeValidator(random.randint(*MaxFileSizeValidator._max_file_size_range))
    mock_field_file = Mock(spec_set=FieldFile)


    def test_validation_for_max_file_size(self) -> None:
        self.mock_field_file.size = self.function.max_file_size
        self.function(self.mock_field_file)


    def test_validation_for_min_size(self) -> None:
        self.mock_field_file.size = self.function._max_file_size_range[0]
        self.function(self.mock_field_file)


    def test_validation_for_invalid_max_file_size(self) -> None:
        self.mock_field_file.size = self.function.max_file_size + random.randint(1, 64)
        with self.assertRaises(ValidationError) as err:
            self.function(self.mock_field_file)
        self.assertEqual(err.exception.args[0], "Ensure that the file size is less than or equal to %(max_size)s bytes.")
        self.assertEqual(err.exception.code, 'file_too_large')
        self.assertEqual(err.exception.params, {'max_size': str(self.function.max_file_size)})
