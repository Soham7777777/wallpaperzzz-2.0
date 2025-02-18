from typing import Any, cast
from unittest.mock import Mock
from django.db import models
import unittest
from adminapp.models import Category
import weakref
from collections.abc import Callable


class TestIsCategoryReceiver(unittest.TestCase):

    from adminapp import signals
    function = signals.delete_category_thumbnail
    (receiver_uid, sender_id), _, _ = next(
        filter(
            lambda receiver:
                    receiver[1]() if isinstance(receiver[1], weakref.ref) else receiver[1]
                    ==
                    function, models.signals.post_delete.receivers
        )
    )


    def test_is_category_receiver(self) -> None:
        self.assertEqual(self.receiver_uid, 'delete_category_thumbnail')
        self.assertEqual(self.sender_id, id(Category))


class TestReceiverFunction(unittest.TestCase):

    from adminapp import signals
    mock_category_instance = Mock(spec_set=Category)    

    def test_function(self) -> None:
        models.signals.post_delete.send(sender=Category, instance=self.mock_category_instance)
        self.mock_category_instance.thumbnail.delete.assert_called_once_with(False)
