from unittest.mock import Mock
from django.test import SimpleTestCase
from common.models import AbstractBaseModel
from common import signals
from django.db import models
from django.db.models.options import Options
from django.db.models.fields.files import FieldFile


class TestDeleteFileOnPostDeleteSignal(SimpleTestCase):

    models.signals.post_delete.connect(signals.delete_file_post_delete_function, sender=AbstractBaseModel, dispatch_uid='TestDeleteFileOnPostDeleteSignalUID')

    mock_model_instance = Mock(
        spec = AbstractBaseModel,
        _meta = Mock(
            spec_set = Options,
            get_fields = Mock(
                return_value = [
                    Mock(
                        spec = models.FileField,
                        get_attname = Mock(return_value='first_file'),
                        verbose_name = Mock(
                            spec_set = str,
                            find = Mock(return_value = 0),
                        ),
                    ),
                    Mock(
                        spec = models.FileField,
                        get_attname = Mock(return_value='second_file'),
                        verbose_name = Mock(
                            spec_set = str,
                            find = Mock(return_value = -1)
                        ),
                    ),
                    Mock(
                        spec = models.Field,
                        get_attname = Mock(return_value='third_file'),
                        verbose_name = Mock(
                            spec_set = str,
                            find = Mock(return_value = 0),
                        ),
                    )
                ],
            ),
        ),
        first_file = Mock(
            spec_set = FieldFile,
        ),
        second_file = Mock(
            spec_set = FieldFile,
        ),
        third_file = Mock(
            spec_set = FieldFile,
        ),
    )
    file1, file2, file3 = mock_model_instance.first_file, mock_model_instance.second_file, mock_model_instance.third_file
    field1, field2, field3 = mock_model_instance._meta.get_fields()
     

    def test_algorithm(self) -> None:
        models.signals.post_delete.send(sender=AbstractBaseModel, instance=self.mock_model_instance)

        self.field1.verbose_name.find.assert_called_once_with(signals.SignalEffect.AUTO_DELETE_FILE)
        self.field2.verbose_name.find.assert_called_once_with(signals.SignalEffect.AUTO_DELETE_FILE)
        self.field3.verbose_name.find.assert_not_called()
        
        self.file3.delete.assert_not_called()
        self.file2.delete.assert_not_called()
        self.file1.delete.assert_called_once_with(save=False)


class TestDeleteOldFileOnPreSaveSignal(SimpleTestCase):

    mock_model_instance = Mock(
        spec = AbstractBaseModel,
        nonull_pk_val = 'nonnull',
        null_pk_val = None,
        _meta = Mock(
            spec = Options,
            pk = Mock(),
            get_fields = Mock(
                return_value = [
                    Mock(
                        spec = models.FileField,
                        get_attname = Mock(return_value='first_file'),
                        verbose_name = Mock(
                            spec_set = str,
                            find = Mock(return_value = 0),
                        ),
                    ),
                    Mock(
                        spec = models.FileField,
                        get_attname = Mock(return_value='second_file'),
                        verbose_name = Mock(
                            spec_set = str,
                            find = Mock(return_value = -1)
                        ),
                    ),
                    Mock(
                        spec = models.Field,
                        get_attname = Mock(return_value='third_file'),
                        verbose_name = Mock(
                            spec_set = str,
                            find = Mock(return_value = 0),
                        ),
                    ),
                ],
            ),
        ),
        first_file = Mock(
            spec_set = FieldFile,
        ),
        second_file = Mock(
            spec_set = FieldFile,
        ),
        third_file = Mock(
            spec_set = FieldFile,
        ),
    )
    sender = Mock(
        spec = type[AbstractBaseModel],
        objects = Mock(
            spec_set = models.Manager,
            get = Mock(
                return_value = mock_model_instance 
            )
        )
    )

    models.signals.pre_save.connect(signals.delete_old_file_pre_save_function, sender=sender, dispatch_uid='TestDeleteOldFileOnPreSaveSignalUID')

    file1, file2, file3 = mock_model_instance.first_file, mock_model_instance.second_file, mock_model_instance.third_file
    field1, field2, field3 = mock_model_instance._meta.get_fields()
    mock_model_instance.reset_mock()


    def test_algorithm(self) -> None:
        self.mock_model_instance._meta.pk.get_attname = Mock(return_value='null_pk_val')
        models.signals.pre_save.send(sender=self.sender, instance=self.mock_model_instance)
        self.mock_model_instance._meta.get_fields.assert_not_called()
        self.mock_model_instance.reset_mock()

        self.mock_model_instance._meta.pk.get_attname = Mock(return_value='nonull_pk_val')
        models.signals.pre_save.send(sender=self.sender, instance=self.mock_model_instance)

        self.sender.objects.get.assert_called_once_with(pk='nonnull')
        self.mock_model_instance._meta.get_fields.assert_called_once()

        self.field1.verbose_name.find.assert_called_once_with(signals.SignalEffect.AUTO_DELETE_OLD_FILE)
        self.field2.verbose_name.find.assert_called_once_with(signals.SignalEffect.AUTO_DELETE_OLD_FILE)
        self.field3.verbose_name.find.assert_not_called()
        
        self.file3.delete.assert_not_called()
        self.file2.delete.assert_not_called()
        self.file1.delete.assert_called_once_with(save=False)
