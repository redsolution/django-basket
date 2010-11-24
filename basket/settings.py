# -*- coding: utf-8 -*-
from django.conf import settings

PRICE_ATTR = getattr(settings, 'BASKET_PRICE_ATTR', 'price')
DEFAULT_BASKET_MODEL = 'basket.models.OrderInfo'
DEFAULT_BASKET_FORM = 'basket.forms.OrderInfoForm'
BASKET_MODEL = getattr(settings, 'BASKET_MODEL', DEFAULT_BASKET_MODEL)
BASKET_FORM = getattr(settings, 'BASKET_FORM', DEFAULT_BASKET_FORM)
