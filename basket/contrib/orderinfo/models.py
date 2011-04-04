# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.signals import post_save
from basket.models import Order
from django.utils.translation import ugettext_lazy as _
from datetime.datetime import now

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
    fio = models.CharField(verbose_name=_('Customer name'), max_length=100,
        blank=True, null=True)
    email = models.EmailField(verbose_name=_('Email'), max_length=100,
        blank=True,null=True)
    telephone = models.CharField(verbose_name=_('Phone number'), max_length=100,
        blank=True, null=True)
    address = models.CharField(verbose_name=_('Address'), max_length=100,
        blank=True, null=True)
    comment = models.CharField(verbose_name=_('Comment'), max_length=200,
        blank=True, null=True)


def connect_to_order(sender, instance, created):
    if created:
        OrderInfo.objects.create(order=instance, registered=now())
post_save.connect(connect_to_order, Order)
