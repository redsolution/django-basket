# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

PRICE_ATTR = getattr(settings, 'BASKET_PRICE_ATTR', 'price')
DEFAULT_BASKET_FORM = 'basket.forms.DefaultOrderForm'

BASKET_FORM = getattr(settings, 'BASKET_FORM', DEFAULT_BASKET_FORM)

BASKET_OPTIONS_USE_KEEP = getattr(settings, 'BASKET_OPTIONS_USE_KEEP', True)
BASKET_OPTIONS_USE_DELETE = getattr(settings, 'BASKET_OPTIONS_USE_DELETE', False)

STATUS_PENDING = 0
STATUS_NEW = 1
STATUS_PROCESS = 2
STATUS_CLOSED = 3
STATUS_ERROR = 4

DEFAULT_ORDER_STATUSES = (
    (STATUS_PENDING, _('Pending')),
    (STATUS_NEW, _('New')),
    (STATUS_PROCESS, _('Process')),
    (STATUS_CLOSED, _('Closed & OK')),
    (STATUS_ERROR, _('Closed with error')),
)
ORDER_STATUSES = getattr(settings, 'ORDER_STATUSES', DEFAULT_ORDER_STATUSES)

DEFAULT_ORDER_EMAIL_SUBJECT = 'New order from site'
ORDER_EMAIL_SUBJECT = getattr(settings, 'ORDER_EMAIL_SUBJECT', DEFAULT_ORDER_EMAIL_SUBJECT)
