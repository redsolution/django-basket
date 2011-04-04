# -*- coding: utf-8 -*-
from django.contrib import admin
from basket.models import Order, Status

class StatusInline(admin.TabularInline):
    model = Status

class OrderAdmin(admin.ModelAdmin):
    inlines = [StatusInline]
    exclude = ['user', 'session', ]
    list_display = ['__unicode__', 'goods', 'summary', 'get_status', 'registered', 'user']
    fieldsets = None
    search_fields = ('user__username',)

try:
    admin.site.register(Order, OrderAdmin)
except admin.sites.AlreadyRegistered:
    pass
