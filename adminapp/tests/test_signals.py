from django.test import SimpleTestCase
from unittest.mock import Mock
from adminapp.models import Category
from django.db import models


class TestCategoryPostDeleteSignal(SimpleTestCase):

    mock_category_instance = Mock(spec_set=Category)    


    def test_function(self) -> None:
        self.mock_category_instance.thumbnail.delete.assert_not_called()
        models.signals.post_delete.send(sender=Category, instance=self.mock_category_instance)
        self.mock_category_instance.thumbnail.delete.assert_called_once_with(False)


class TestCategoryPreDeleteSignal(SimpleTestCase):

    mock_category_instance = Mock(spec_set=Category)


    def test_create_without_delete(self) -> None:
        self.mock_category_instance.thumbnail.delete.assert_not_called()
        self.mock_category_instance.id = None
        models.signals.pre_save.send(sender=Category, instance=self.mock_category_instance)
        self.mock_category_instance.thumbnail.delete.assert_not_called()


    def test_delete_on_update(self) -> None:
        raise NotImplementedError("deletion of old thumbnail is not tested")
