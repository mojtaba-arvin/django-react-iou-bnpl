from django.apps import AppConfig


class MerchantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'merchant'

    def ready(self):
        import merchant.signals  # noqa
