from typing import Any
from unittest.mock import Mock, patch
from django.apps import apps
from django.db import models
import unittest
from adminapp.models import Category
from django.db.models.signals import post_delete
from adminapp import signals


class TestSignalRegisteredInReady(unittest.TestCase):
    
    def setUp(self) -> None:
        self.ready_method = apps.get_app_config('adminapp').ready
    

    @patch('adminapp.apps.post_delete', spec_set=post_delete)
    def test_signal_registered_in_ready(self, mock_post_delete: Any) -> None:
        mock_post_delete.connect.assert_not_called()
        self.ready_method()
        mock_post_delete.connect.assert_called_once_with(signals.delete_category_thumbnail, sender='adminapp.Category', dispatch_uid='delete_category_thumbnail')


class TestReceiverFunction(unittest.TestCase):

    mock_category_instance = Mock(spec_set=Category)    


    def test_function(self) -> None:
        self.mock_category_instance.thumbnail.delete.assert_not_called()
        models.signals.post_delete.send(sender=Category, instance=self.mock_category_instance)
        self.mock_category_instance.thumbnail.delete.assert_called_once_with(False)
