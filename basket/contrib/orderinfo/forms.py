# -*- coding: utf-8 -*-
from django import forms
from models import OrderInfo

class OrderInfoForm(forms.ModelForm):
    class Meta:
        model = OrderInfo
        exclude = ['order']

    def __init__(self, request, *args, **kwds):
        kwds.update({
            'instance': OrderInfo(order=request.order),
        })
        return super(OrderInfoForm, self).__init__(*args, **kwds)
