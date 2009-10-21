# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import inlineformset_factory
from models import Basket, BasketItem


class BaseBasketForm(forms.ModelForm):
    '''
    Base basket form. I fyou want to override default fields,
    set BASKET_FORM in settings.py. Fields will be merged with 
    this base form. For more information check default settings
    in basket/settings.py
    '''
    class Meta:
        model = Basket
        exclude = ('user', 'session', 'anonymous')


class BasketForm(BaseBasketForm):
    def __init__(self, *args, **kwds):
        user = kwds.pop('user', None)
        if not user.is_anonymous():
            if user.userprofile_set.all().count() != 0:
                profile = user.get_profile()
                kwds.update({
                    'initial': {
                        'contact': '%s (%s)' % (profile.contact, user.first_name),
                        'contact_time': profile.contact_time,
                        'address': profile.address,
                    }
                })
        super(BasketForm, self).__init__(*args, **kwds)

    contact = forms.CharField(label=u'Ваш телефон', max_length=200)
    contact_time = forms.CharField(label=u'Удобное время для связи с вами',
        max_length=200, required=False)
    address = forms.CharField(label=u'Адрес для доставки', max_length=200)
    comment = forms.CharField(label=u'Комментарии', help_text='Поле не обязательное',
       max_length=200, required=False)
    use_discount = forms.BooleanField(label=u'Использовать накопленную скидку',
        required=False)

BasketFormset = inlineformset_factory(Basket, BasketItem, extra=0, max_num=10,
    can_delete = True)
