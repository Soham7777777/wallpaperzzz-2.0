from unittest.mock import patch
from django.test import SimpleTestCase
from common.utils import get_file_extensions_for_image_type, ImageType


class TestGetFileExtensionForImageType(SimpleTestCase):


    def test_function(self) -> None:
        from common.utils import _file_extensions_for_image_type
        for image_type in ImageType:
            with self.subTest(image_type=image_type):
                self.assertEqual(get_file_extensions_for_image_type(image_type), _file_extensions_for_image_type[image_type])
