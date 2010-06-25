# -*- coding: utf-8 -*-
from django.contrib import admin
from basket.models import Order, Status, OrderStatus


class StatusInline(admin.TabularInline):
    model = OrderStatus
    extra = 1
    fields = ('type', 'order', 'date', 'comment')
    template = 'admin/basket/order/tabular.html'


class OrderAdmin(admin.ModelAdmin):
    inlines = [StatusInline, ]
    exclude = ['user', 'session', 'form_data']
    list_display = ['__unicode__', 'goods', 'price', 'get_status', 'registered', 'user']
    fieldsets = None
    list_filter = ['status', ]

    def save_formset(self, request, form, formset, change):

        # override: last edited user saved in user field
        for index, inline_form in enumerate(formset.forms):
            if inline_form.changed_data:
                formset.cleaned_data[index].update({'user': request.user})

        return super(OrderAdmin, self).save_formset(request, form, formset, change)

try:
    admin.site.register(Order, OrderAdmin)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(Status)
except admin.sites.AlreadyRegistered:
    pass
