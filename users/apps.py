from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        autodiscover_modules('init_admin.py')
