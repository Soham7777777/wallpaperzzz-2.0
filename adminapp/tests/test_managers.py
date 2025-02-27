from unittest.mock import Mock, patch
from django.test import SimpleTestCase
from adminapp.models import SettingsManager


class TestSettingsManager(SimpleTestCase):

    settings_manager = SettingsManager()

    
    @patch.object(SettingsManager, 'get_or_create')
    def test_get(self, mock_get_or_create: Mock) -> None:
        mock_get_or_create.return_value = 'somevalue', True
        self.assertEqual(self.settings_manager.get(), 'somevalue')
        mock_get_or_create.assert_called_once_with(key='BASE_SETTINGS')
