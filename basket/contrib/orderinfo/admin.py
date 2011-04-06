# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
from basket.models import Order
from basket.contrib.orderinfo.models import OrderInfo
#from django.utils.translation import ugettext_lazy as _


class InfoInline(admin.StackedInline):
    extra = 0
    max_num = 1
    can_delete = False
    model = OrderInfo


class OrderInfoAdmin(admin.ModelAdmin):
    inlines = [InfoInline]
    exclude = ['user', 'session_key', ]
    list_display = ['__unicode__', 'goods', 'summary', 'get_status', 'registered', 'user']
    fieldsets = None
    search_fields = ('user__username',)


try:
    admin.site.unregister(Order)
    admin.site.register(Order, OrderInfoAdmin)
except admin.sites.AlreadyRegistered:
    pass
