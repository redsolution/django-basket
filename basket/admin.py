# -*- coding: utf-8 -*-
from django.contrib import admin
from basket.models import Order, Status, OrderStatus


class StatusInline(admin.TabularInline):
    model = OrderStatus
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    inlines = [StatusInline, ]
    exclude = ['user', 'session']
    list_display = ['__unicode__', 'goods', 'price', 'get_status', 'registered', 'user']
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
