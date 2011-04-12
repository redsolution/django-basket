# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import inlineformset_factory
from django.contrib.contenttypes.models import ContentType
from basket.models import Order, BasketItem
from basket.settings import BASKET_OPTIONS_USE_KEEP
from django.utils.translation import ugettext_lazy as _


class BasketItemForm(forms.ModelForm):
    class Meta:
        model = BasketItem

    content_type = forms.ModelChoiceField(queryset=ContentType.objects.all(),
        widget=forms.HiddenInput)
    object_id = forms.IntegerField(widget=forms.HiddenInput)
    if BASKET_OPTIONS_USE_KEEP:
        keep = forms.BooleanField(initial=True, required=False)

    def save(self, *args, **kwargs):
        if BASKET_OPTIONS_USE_KEEP:
            if not self.cleaned_data.get('keep', False):
                self.cleaned_data['quantity'] = 0
        self.instance.order.set_quantity(self.instance.content_object,
            self.cleaned_data.get('quantity', 0))

OrderFormset = inlineformset_factory(Order, BasketItem, extra=0,
    can_delete=False, form=BasketItemForm)


class DefaultOrderForm(forms.Form):
    name = forms.CharField(label=_('Customer name'), max_length=100)
    phone = forms.CharField(label=_('Customer phone'), max_length=100)
    address = forms.CharField(label=_('Delivery address'), max_length=255)
    contact_time = forms.CharField(label=_('Convenient time to call'),
        max_length=50, required=False)
    comment = forms.CharField(label=_('Comment for us'), max_length=255,
        widget=forms.Textarea(), required=False)

    def __init__(self, request, *args, **kwds):
        return super(DefaultOrderForm, self).__init__(*args, **kwds)
