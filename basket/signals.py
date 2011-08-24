# -*- coding: utf-8 -*-
from basket.models import STATUS_NEW, Order
from basket.utils import get_order_form, send_mail
from django.conf import settings
from django.template import loader
from django.utils.translation import ugettext
import django.dispatch
from models import Order


order_submit = django.dispatch.Signal(providing_args=["order", "data"])


def comment_order(order, form_data):
    OrderForm = get_order_form()
    result = {}
    for field_name, value in form_data.iteritems():
        result.update({
            field_name: (value, OrderForm.base_fields[field_name].label),
        })

    message = loader.render_to_string('basket/order.txt', {
        'order': order,
        'form_data': result,
    })
    return message

def email_to_managers(sender, **kwargs):
    '''Send email when order issued'''
    managers = [manager[1] for manager in settings.MANAGERS]
    subject = _('New order from site')

    order = kwargs['order']
    form_data = kwargs['data']
    message = comment_order(order, form_data)
    send_mail(subject, message, managers)

def change_status(sender, **kwargs):
    order = kwargs['order']
    order.comment = _('Automatically created status')
    order.status = STATUS_NEW
    order.save()

def autocomment(sender, **kwargs):
    order = kwargs['order']
    form_data = kwargs['data']
    order.comment = '\n'.join((
        '%s' % order.comment,
        comment_order(order, form_data),
        ugettext('New order'),
    ))
    order.save()

order_submit.connect(email_to_managers, sender=Order)
order_submit.connect(change_status, sender=Order)
order_submit.connect(autocomment, sender=Order)
