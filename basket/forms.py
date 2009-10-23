# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import inlineformset_factory
from models import Basket, BasketItem
from basket.utils import import_item
from basket import settings as basket_settings
from django.contrib.contenttypes.models import ContentType


class BaseBasketForm(forms.ModelForm):
    '''
    Base basket form. I fyou want to override default fields,
    set BASKET_FORM in settings.py. Fields will be merged with 
    this base form. For more information check default settings
    in basket/settings.py
    '''
    class Meta:
        model = Basket
        exclude = ('user', 'session', 'anonymous', 'order_date', 'delivery_date', 'delivered')


class ContactBasketForm(forms.ModelForm):
    contact = forms.CharField(label=u'Ваш телефон', max_length=200)
    contact_time = forms.CharField(label=u'Удобное время для связи с вами',
        max_length=200, required=False)
    address = forms.CharField(label=u'Адрес для доставки', max_length=200)
    comment = forms.CharField(label=u'Комментарии', help_text='Поле не обязательное',
       max_length=200, required=False)

extend_form_class = import_item(basket_settings.BASKET_FORM, 'Can not import BASKET_FORM')

class BasketForm(extend_form_class, BaseBasketForm):
    pass


class BasketItemForm(forms.ModelForm):
    class Meta:
        model = BasketItem
    
    basket = forms.CharField(max_length=100, widget=forms.HiddenInput)
    content_type = forms.ModelChoiceField(queryset=ContentType.objects.all(), 
        widget=forms.HiddenInput)
    object_id = forms.IntegerField(widget=forms.HiddenInput)
    keep = forms.BooleanField(initial=True, required=False)
    
BasketFormset = inlineformset_factory(Basket, BasketItem, extra=0, max_num=10,
    can_delete=False, form=BasketItemForm)
