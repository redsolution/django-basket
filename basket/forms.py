# -*- coding: utf-8 -*-
from basket.models import Order, BasketItem
from basket.settings import BASKET_OPTIONS_USE_KEEP
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import inlineformset_factory
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

class AddItemForm(forms.Form):
    '''
    This form supposed to be used in template tag, for user input 
    validation in add-to-basket POSTs'
    '''
    content_type = forms.ModelChoiceField(queryset=ContentType.objects.all(),
         label='Content type ID', widget=forms.HiddenInput())
    object_id = forms.IntegerField(label='Object ID', widget=forms.HiddenInput())
    quantity = forms.IntegerField(label='Quantity', widget=forms.HiddenInput(),
        initial=1)

    def __init__(self, order, *args, **kwds):
        self.order = order
        return super(AddItemForm, self).__init__(*args, **kwds)

    @classmethod
    def for_object(cls, instance):
        '''
        Returns ``AddItemForm`` instance with bound fields generated for 
        given object.
        The form instance has ``order`` attribute equal None. But it should 
        not be taken into account, because this method supposed to be used only
        for form displaying, not processing.
        Did you read it? Do not use this method in form processing!
        '''
        content_type = ContentType.objects.get_for_model(instance)
        initial = {
            'content_type': content_type.id,
            'object_id': instance.id,
            'quantity': cls.base_fields['quantity'].initial,
        }
        return cls(None, initial=initial)

    def save(self):
        try:
            content_type = ContentType.objects.get(id=self.cleaned_data['content_type'])
            item = content_type.get_object_for_this_type(id=self.cleaned_data['object_id'])
        except ObjectDoesNotExist:
            return 0
        return self.order.add_item(item, self.cleaned_data['quantity'])


