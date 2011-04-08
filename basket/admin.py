# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
from django import forms
from basket.models import Order
from django.utils.translation import ugettext_lazy as _


class CommentForm(forms.ModelForm):
    class Meta:
        model = Order

class OrderAdmin(admin.ModelAdmin):
    model = Order
    form = CommentForm
    exclude = ['user', 'session_key', ]
    list_display = ['__unicode__', 'goods', 'summary', 'status', 'registered', 'user']
    list_filter = ['status']
    fieldsets = (
        (_('Order data'), {
            'classes': ('collapse',),
            'fields': ('status', 'created', 'comment'),
        }),
    )
    search_fields = ('user__username',)


try:
    admin.site.register(Order, OrderAdmin)
except admin.sites.AlreadyRegistered:
    pass
