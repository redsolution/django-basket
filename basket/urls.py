# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'basket.views.show_basket', name='basket'),
    url(r'^confirm/$', 'basket.views.confirm', name='confirm'),
    url(r'^add/$', 'basket.views.add_to_basket', name='add_to_basket'),
    url(r'^status/$', 'basket.views.order_status', name='order_status'),
    url(r'^thankyou/$', 'basket.views.thankyou', name='thankyou'),
    # direct to templates:
    url(r'^ajax/$', 'django.views.generic.simple.direct_to_template',
        {'template': 'basket/basket_panel.html'}, name='ajax_basket'),
)
