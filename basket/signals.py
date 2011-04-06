# -*- coding: utf-8 -*-
import django.dispatch

order_submit = django.dispatch.Signal(providing_args=["order", "data"])
