# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
from basket.models import Order, Status
from django.utils.translation import ugettext_lazy as _


class StatusInline(admin.TabularInline):
    model = Status
    extra = 0
    fields = ('status', 'order', 'modified', 'comment',)


class OrderAdmin(admin.ModelAdmin):
    inlines = [StatusInline]
    exclude = ['user', 'session_key', ]
    list_display = ['__unicode__', 'goods', 'summary', 'get_status', 'registered', 'user']
    fieldsets = None
    search_fields = ('user__username',)


try:
    admin.site.register(Order, OrderAdmin)
except admin.sites.AlreadyRegistered:
    pass
