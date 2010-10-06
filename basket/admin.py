# -*- coding: utf-8 -*-
from django.contrib import admin
from basket.models import Order, Status, OrderStatus, States, \
    get_order_info_class, ACTION_AND_STATE_CHOICES
from django import forms
from django.forms.models import BaseInlineFormSet
import json
import datetime

class StatusInlineForm(forms.ModelForm):
    class Meta:
        model = OrderStatus
        fields = ('type', 'order', 'date', 'comment', 'user')
    user = forms.CharField(label=u'Пользователь',
        widget=forms.HiddenInput(attrs={'disabled': True}), required=False)

class StatusInline(admin.TabularInline):
    model = OrderStatus
    extra = 1
    form = StatusInlineForm
    fields = ('type', 'order', 'date', 'comment', 'user')
    template = 'admin/basket/order/tabular.html'

class OrderInfoInline(admin.StackedInline):
    model = get_order_info_class()
    extra = 1


class StatesInlineFormset(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(StatesInlineFormset, self).__init__(*args, **kwargs)
        self.can_delete = False

class StatesInline(admin.TabularInline):
    model = States
    extra = 1
    formset = StatesInlineFormset

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderInfoInline, StatesInline]
    exclude = ['user', 'session', 'form_data']
    list_display = ['__unicode__', 'goods', 'price', 'get_status', 'registered', 'user']
    fieldsets = None
    list_filter = ['status', ]
    search_fields = ('user__username',)

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        urlpatterns = patterns('',
            url(r'^basket/order/(?P<object_id>\d+)/$',
                self.admin_site.admin_view(self.change_view), name='status'),
        )
        return urlpatterns + super(ChildAdmin, self).get_urls()

    def change_view(self, request, object_id):
        from django.contrib.admin.views.main import ChangeList

        context = {'actions_with_states': json.dumps(ACTION_AND_STATE_CHOICES)}

        return admin.ModelAdmin.change_view(self, request, object_id=object_id,
                                            extra_context=context)

    def save_formset(self, request, form, formset, change):
        # override: last edited user saved in user field
        for index, inline_form in enumerate(formset.forms):

            if inline_form.has_changed():
                if 'modified' in inline_form.changed_data:
                    inline_form.changed_data.remove('modified')
                formset.cleaned_data[index].update({'modified': "%s %s" % (request.user.username, datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S"))})

        return super(OrderAdmin, self).save_formset(request, form, formset, change)

try:
    admin.site.register(Order, OrderAdmin)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(Status)
except admin.sites.AlreadyRegistered:
    pass
