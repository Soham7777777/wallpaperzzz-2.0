from django.apps import AppConfig
from django.db.models.signals import post_delete, pre_save


class AdminappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'adminapp'


    def ready(self) -> None:
        from . import signals

        post_delete.connect(signals.delete_category_thumbnail, sender='adminapp.Category', dispatch_uid='delete_category_thumbnail')

        pre_save.connect(signals.delete_old_category_thumbnail, sender='adminapp.Category', dispatch_uid='delete_old_category_thumbnail')
