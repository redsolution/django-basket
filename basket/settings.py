# -*- coding: utf-8 -*-
from django.conf import settings


DEFAULT_BASKET_FORM = 'basket.forms.ContactForm'
BASKET_FORM = getattr(settings, 'BASKET_FORM', DEFAULT_BASKET_FORM)
PRICE_ATTR = getattr(settings, 'BASKET_PRICE_ATTR', 'price')
DEFAULT_BASKET_ORDERINFO = 'basket.models.OrderInfo'
BASKET_ORDERINFO = getattr(settings, 'BASKET_ORDERINFO', DEFAULT_BASKET_ORDERINFO)
