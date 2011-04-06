# -*- coding: utf-8 -*-
from basket.models import Order
from basket.signals import order_submit
from basket import settings as basket_settings
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

class OrderInfo(models.Model):
    '''
    Order information model. If you want to override default fields, set BASKET_MODEL in settings.py.
    For more information check default settings in basket/settings.py
    '''
    class Meta:
        verbose_name = _('Order information')
        verbose_name_plural = _('Order information')

    order = models.OneToOneField(Order)
    registered = models.DateTimeField(verbose_name=_('Order creation date and time'),
        auto_now_add=True)
    name = models.CharField(verbose_name=_('Customer name'), max_length=100)
    address = models.CharField(verbose_name=_('Address'), max_length=100)
    city = models.CharField(verbose_name=_('City'), max_length=50)
    telephone = models.CharField(verbose_name=_('Phone number'), max_length=100)

    email = models.EmailField(verbose_name=_('Email'), max_length=100,
        blank=True, null=True)
    comment = models.CharField(verbose_name=_('Comment'), max_length=200,
        blank=True, null=True)


def add_orderinfo(sender, **kwargs):
    order = kwargs['order']
    cleaned_data = kwargs['data']
    cleaned_data.update({
        'order': order,
    })
    OrderInfo.objects.create(**cleaned_data)

order_submit.connect(add_orderinfo, sender=Order)

if basket_settings.BASKET_FORM == basket_settings.DEFAULT_BASKET_FORM:
    basket_settings.BASKET_FORM = 'basket.contrib.orderinfo.forms.OrderInfoForm'
