# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'basket.views.show_basket', name='basket'),
    url(r'^ajax/$', 'basket.views.ajax_basket', name='ajax_basket'),
    url(r'^thankyou/$', 'basket.views.thankyou', name='thankyou'),
    url(r'^confirm/$', 'basket.views.confirm', name='confirm'),
    url(r'^add/$', 'basket.views.add_to_basket', name='add_to_basket'),
)