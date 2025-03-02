from unittest.mock import Mock, patch
from django.test import SimpleTestCase
from adminapp.models import SettingsStore
from common.models import AbstractBaseModel
from django.db import models
from common.utils import ImageType, get_file_extensions_for_image_type
from adminapp.models import _SettingsManager



class TestFetchSettingsMethod(SimpleTestCase):

    @patch.object(_SettingsManager, 'get_or_create', return_value=('somevalue', True))
    def test_get(self, mock_get_or_create: Mock) -> None:
        self.assertEqual(_SettingsManager().fetch_settings(), 'somevalue')
        mock_get_or_create.assert_called_once_with(key='BASE_SETTINGS')


class TestFetchAllowedImageFileExtensions(SimpleTestCase):

    _mock_fields = [
        Mock(
            spec = models.BooleanField,
            db_column = ImageType.PNG,
        ),
        Mock(
            spec = models.BooleanField,
            db_column = ImageType.JPEG,
        ),
        Mock(
            spec = models.BooleanField,
            db_column = ImageType.TIFF,
        ),
        Mock(
            spec = models.BooleanField,
            db_column = 'webp',
        ),
        Mock(
            spec = models.CharField,
            db_column = 'text'
        )
    ]

    _mock_fields[0].name = 'png'
    _mock_fields[1].name = 'jpeg'
    _mock_fields[2].name = 'tiff'
    _mock_fields[3].name = 'webp'
    _mock_fields[4].name = 'text'

    mock_get_fields = Mock(
        name='mock_get_fields',
        return_value = _mock_fields
    )

    mock_settings_store = Mock(
        name='mock_settings_store',
        spec = AbstractBaseModel,
        png = True,
        jpeg = True,
        tiff = False,
        webp = True,
        text = None,
    )


    @patch('adminapp.models.SettingsStore._meta', get_fields=mock_get_fields)
    @patch('adminapp.models._SettingsManager.get_or_create', return_value=(mock_settings_store, True))
    def test_function(self, mock_get_or_create: Mock, mock_meta: Mock) -> None:
        self.assertEqual(
            _SettingsManager().fetch_allowed_image_file_extensions(),
            (
                *get_file_extensions_for_image_type(ImageType.PNG),
                *get_file_extensions_for_image_type(ImageType.JPEG),
            )
        )
