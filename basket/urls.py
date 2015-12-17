# -*- coding: utf-8 -*-
from django.conf.urls import *
from basket.settings import BASKET_OPTIONS_USE_DELETE
from django.views.generic import TemplateView

urlpatterns = patterns('basket.views',
    url(r'^$', 'basket', name='basket'),
    url(r'^confirm/$', 'confirm', name='order_confirm'),
    url(r'^add/$', 'add_to_basket', name='add_to_basket'),
)

if BASKET_OPTIONS_USE_DELETE:
    urlpatterns += patterns('basket.views',
        url(r'^delete/$', 'delete_from_basket', name='del_from_basket'),
    )

urlpatterns += patterns('django.views.generic.simple',
    url(r'^thankyou/$', TemplateView.as_view(template_name='basket/thankyou.html'),
        name='basket-thankyou'),
    url(r'^empty/$', TemplateView.as_view(template_name='basket/empty.html'),
        name='basket-empty'),
)
