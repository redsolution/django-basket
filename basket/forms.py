# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.forms.models import inlineformset_factory
from django.template import loader
from django.contrib.contenttypes.models import ContentType
from basket.models import Order, BasketItem, get_order_info_class
from basket.utils import import_item, send_mail
from basket.settings import BASKET_FORM
from django.utils import simplejson
from django.core.exceptions import ImproperlyConfigured
import datetime

class OrderForm(forms.ModelForm):
    '''
    Order basket form. If you want to override default fields,
    set BASKET_FORM in settings.py. Fields will be merged with 
    this base form. For more information check default settings
    in basket/settings.py
    '''
    class Meta:
        model = get_order_info_class()
        exclude = ('order', 'trans_company', 'delivery_type', 'delivery_cost',
                   'delivery_datetime')

def get_order_form():
    try:
        form_class = import_item(BASKET_FORM, 'Can not import BASKET_FORM')
    except ImproperlyConfigured:
        return OrderForm
    else:
        return form_class

class OrderStatusForm(forms.Form):
    order_id = forms.IntegerField(label=u'Номер закза')

class BasketItemForm(forms.ModelForm):
    class Meta:
        model = BasketItem

    order = forms.CharField(max_length=100, widget=forms.HiddenInput)
    content_type = forms.ModelChoiceField(queryset=ContentType.objects.all(),
        widget=forms.HiddenInput)
    object_id = forms.IntegerField(widget=forms.HiddenInput)
    keep = forms.BooleanField(initial=True, required=False)

OrderFormset = inlineformset_factory(Order, BasketItem, extra=0,
    can_delete=False, form=BasketItemForm)
