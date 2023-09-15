from django.apps import AppConfig  # type: ignore


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'poster'

    def ready(self):
        import poster.signals # NOQA
        import poster.receivers # NOQA
