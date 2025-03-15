from django.apps import AppConfig
from django.db.models.signals import post_delete, pre_save


class AdminappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'adminapp'


    def ready(self) -> None:
        from common import signals

        post_delete.connect(signals.delete_file_post_delete_function, sender='adminapp.Category', dispatch_uid='CATEGORY_DELETE_FILES_POST_DELETE')

        post_delete.connect(signals.delete_file_post_delete_function, sender='adminapp.Wallpaper', dispatch_uid='WALLPAPER_DELETE_FILES_POST_DELETE')


        pre_save.connect(signals.delete_old_file_pre_save_function, sender='adminapp.Category', dispatch_uid='CATEGORY_DELETE_OLD_FILES_PRE_SAVE')

        pre_save.connect(signals.delete_old_file_pre_save_function, sender='adminapp.Wallpaper', dispatch_uid='WALLPAPER_DELETE_OLD_FILES_PRE_SAVE')
