from django.apps import AppConfig


class DjangoExpensesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_expenses"
    verbose_name = "Expenses"

    def ready(self):
        from . import receivers
        try:
            from .api import urls
        except ImportError:
            pass
