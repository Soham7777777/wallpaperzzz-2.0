from unittest.mock import Mock
from django.test import SimpleTestCase
from common.utils import ImageType, get_file_extensions_for_image_type
from common.validators import ImageTypeFileExtensionsValidator
from django.db.models.fields.files import ImageFieldFile
from django.core.exceptions import ValidationError


class TestImageTypeFileExtensionsValidator(SimpleTestCase):
    
    mock_image_field_file = Mock(spec_set=ImageFieldFile)
    image_type_file_extension_validator = ImageTypeFileExtensionsValidator((ImageType.PNG, ImageType.JPEG))


    def test_validation_for_valid_extensions(self) -> None:
        for extension in get_file_extensions_for_image_type(ImageType.PNG):
            self.mock_image_field_file.path = 'some/path/name' + extension
            self.image_type_file_extension_validator(self.mock_image_field_file)

        for extension in get_file_extensions_for_image_type(ImageType.JPEG):
            self.mock_image_field_file.path = 'some/path/name' + extension
            self.image_type_file_extension_validator(self.mock_image_field_file)


    def test_validation_for_invalid_extension(self) -> None:
        self.mock_image_field_file.path = 'some/path/name' + '.notpng'
        with self.assertRaises(ValidationError) as err:
            self.image_type_file_extension_validator(self.mock_image_field_file)
        self.assertEqual(err.exception.args[0], "Ensure that the image file has an extension from the supported file extensions: %(extensions)s for image types: %(image_type)s.")
        self.assertEqual(err.exception.code, 'invalid_image_extension')
        self.assertEqual(err.exception.params, {'extensions': (*get_file_extensions_for_image_type(ImageType.PNG), *get_file_extensions_for_image_type(ImageType.JPEG)), 'image_type': (ImageType.PNG, ImageType.JPEG)})
