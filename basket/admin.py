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
    list_display = ['__unicode__', 'total_admin', 'status', 'registered', 'user']
    list_filter = ['status']
    fieldsets = (
        (_('Order data'), {
            'classes': ('collapse',),
            'fields': ('status', 'created', 'comment'),
        }),
    )
    search_fields = ('user__username',)

    def total_admin(self, obj):
        return _('items: <strong>%(count)s</strong>, price: <strong>%(price)s</strong>' % obj.total())
    total_admin.short_description = _('Quantity info')
    total_admin.allow_tags = True

try:
    admin.site.register(Order, OrderAdmin)
except admin.sites.AlreadyRegistered:
    pass
