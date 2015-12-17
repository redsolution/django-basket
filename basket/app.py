from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class BasketAppConfig(AppConfig):
    name = 'basket'
    verbose_name = _('Basket')

    class Meta:
        app_label = 'basket'