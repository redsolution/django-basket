# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
from basket.models import Order, Status, OrderStatus, BasketItem, get_status_types
from django.forms.models import save_instance


class StatusInline(admin.TabularInline):
    model = OrderStatus
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    inlines = [StatusInline, ]
    exclude = ['user', 'session']
    list_display = ['__unicode__', 'goods', 'price', 'get_status']
    fieldsets = None
    list_filter = ['status', ]


try:
    admin.site.register(Order, OrderAdmin)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(Status)
except admin.sites.AlreadyRegistered:
    pass
