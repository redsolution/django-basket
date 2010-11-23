# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'basket.views.basket', name='basket'),
    url(r'^confirm/$', 'basket.views.confirm', name='order_confirm'),
    url(r'^status/$', 'basket.views.status', name='order_status'),
    url(r'^thankyou/$', 'basket.views.thankyou', name='order_thankyou'),
    url(r'^add/$', 'basket.views.add_to_basket', name='add_to_basket'),
)
