# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import inlineformset_factory
from django.contrib.contenttypes.models import ContentType
from basket.models import Order, BasketItem, get_order_model
from basket.utils import import_item
from basket.settings import BASKET_FORM
from django.core.exceptions import ImproperlyConfigured

class OrderInfoForm(forms.ModelForm):
    '''
    Order info form. If you want to override default fields, set BASKET_FORM in settings.py.
    For more information check default settings in basket/settings.py
    '''
    class Meta:
        model = get_order_model()
        exclude = ['order']

    def clean(self):
        cleaned_data = super(OrderInfoForm, self).clean()
        if not cleaned_data.get('email') and not cleaned_data.get('telephone'):
            raise forms.ValidationError(u'Необходимо заполнить E-mail или телефон')
        return cleaned_data

def get_order_form():
    try:
        form_class = import_item(BASKET_FORM, 'Can not import BASKET_FORM')
    except ImproperlyConfigured:
        return OrderInfoForm
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

    def save(self, *args, **kwargs):
        if not self.cleaned_data.get('keep', False):
            self.cleaned_data['quantity'] = 0
        self.instance.order.set_quantity(self.instance.content_object,
            self.cleaned_data.get('quantity', 0))

OrderFormset = inlineformset_factory(Order, BasketItem, extra=0,
    can_delete=False, form=BasketItemForm)
