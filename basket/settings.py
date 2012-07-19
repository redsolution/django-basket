# -*- coding: utf-8 -*-
from django.conf import settings

PRICE_ATTR = getattr(settings, 'BASKET_PRICE_ATTR', 'price')
DEFAULT_BASKET_FORM = 'basket.forms.DefaultOrderForm'

BASKET_FORM = getattr(settings, 'BASKET_FORM', DEFAULT_BASKET_FORM)

BASKET_OPTIONS_USE_KEEP = getattr(settings, 'BASKET_OPTIONS_USE_KEEP', True)
BASKET_OPTIONS_USE_DELETE = getattr(settings, 'BASKET_OPTIONS_USE_DELETE', False)

DEFAULT_ORDER_STATUSES = 'basket.models.STATUS_CHIOCES'
ORDER_STATUSES = getattr(settings, 'ORDER_STATUSES', DEFAULT_ORDER_STATUSES)