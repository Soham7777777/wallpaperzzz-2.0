from unittest.mock import Mock, create_autospec, patch
from django.test import SimpleTestCase
from adminapp.models import SettingsStore, validate_image_file_extensions, validate_image_max_file_size
from django.db.models.fields.files import ImageFieldFile


class TestDynamicMaxFileSizeValidator(SimpleTestCase):

    mock_image_field_file_instance = create_autospec(ImageFieldFile, instance=True)
    mock_settings_store_instance = create_autospec(SettingsStore, instance=True, maximum_image_file_size=1)
    mock_validator_function = Mock()
    

    @patch('adminapp.models.MaxFileSizeValidator', return_value=mock_validator_function)
    @patch('adminapp.models.SettingsStore.settings.fetch_settings', return_value = mock_settings_store_instance)
    def test_function(self, mock_fetch_settings_method: Mock, mock_max_file_size_validator_class: Mock) -> None:
        validate_image_max_file_size(self.mock_image_field_file_instance)
        mock_max_file_size_validator_class.assert_called_once_with(1024)
        self.mock_validator_function.assert_called_once_with(self.mock_image_field_file_instance)


class TestDynamicImageFileExtensionsValidator(SimpleTestCase):

    mock_image_field_file_instance = create_autospec(ImageFieldFile, instance=True)
    mock_extensions = Mock()
    mock_validator_function = Mock()


    @patch('adminapp.models.validators.FileExtensionValidator', return_value=mock_validator_function)
    @patch('adminapp.models.SettingsStore.settings.fetch_allowed_image_file_extensions', return_value = mock_extensions)
    def test_function(self, mock_fetch_allowed_image_file_extensions: Mock, mock_file_extension_validator_class: Mock) -> None:
        validate_image_file_extensions(self.mock_image_field_file_instance)
        mock_file_extension_validator_class.assert_called_once_with(self.mock_extensions)
        self.mock_validator_function.assert_called_once_with(self.mock_image_field_file_instance)
