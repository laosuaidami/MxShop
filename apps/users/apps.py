from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'
    verbose_name = u"用户管理"

    def ready(self):
        import users.signals
