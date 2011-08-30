# -*- coding: utf-8 -*-
from basket.forms import OrderFormset, AddItemForm
from basket.models import Order
from basket.settings import BASKET_OPTIONS_USE_KEEP, BASKET_OPTIONS_USE_DELETE
from basket.signals import order_submit
from basket.utils import render_to, get_order_form, send_mail
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest, HttpResponseRedirect, Http404
from django.template import loader
from django.views.decorators.http import require_http_methods
import simplejson
from django.shortcuts import render_to_response


@render_to('basket/basket.html')
def basket(request):
    # do not create order automatically
    order = request.order
    if order is None or order.total['count'] == 0:
        return HttpResponseRedirect(reverse('basket-empty'))


    if request.method == 'POST':
        formset = OrderFormset(request.POST, instance=order)

        if formset.is_valid():
            formset.save()

            if 'refresh' in request.POST:
                return HttpResponseRedirect(reverse('basket'))
            else:
                return HttpResponseRedirect(reverse('order_confirm'))
    else:
        formset = OrderFormset(instance=order)

    return {
        'formset': formset,
        'keep': BASKET_OPTIONS_USE_KEEP,
        'delete': BASKET_OPTIONS_USE_DELETE,
    }

@render_to('basket/confirm.html')
def confirm(request):
    # do not create order automatically
    order = request.order

    if order is None or order.empty():
        return HttpResponseRedirect(reverse('basket-empty'))

    if request.method == 'POST':
        form = get_order_form()(request, request.POST)
        if form.is_valid():
            order_submit.send(sender=Order, order=order, data=form.cleaned_data)
            return HttpResponseRedirect(reverse('basket-thankyou'))
    else:
        form = get_order_form()(request)
    return {
        'form': form,
        'order': order,
    }

def thankyou(request):
    '''Use generic view instead'''
    raise NotImplementedError

def status(request, order_id=None):
    '''Use generic view instead'''
    raise NotImplementedError

@require_http_methods(["POST"])
def add_to_basket(request):
    # Automatically create order if it does not exist
    if request.order is None:
        order = Order.from_request(request)
        request.order = order
    else:
        order = request.order

    if request.method == 'POST':
        form = AddItemForm(order, request.POST)
        if form.is_valid():
            form.save()
        else:
            return HttpResponseBadRequest(form.errors)
    if request.is_ajax():
        return render_to_response('basket/summary.html', {})
    else:
        return HttpResponseRedirect(reverse('basket'))


@require_http_methods(["POST"])
@render_to('basket/summary.html')
def delete_from_basket(request):
    # Do not automatically create order
    order = request.order
    if order is None:
        raise Http404(_('Basket does not exist'))

    content_type_id = request.REQUEST.get('content_type', None)
    object_id = request.REQUEST.get('object_id', None)
    try:
        content_type = ContentType.objects.get(id=content_type_id)
        item = content_type.get_object_for_this_type(id=object_id)
    except ObjectDoesNotExist:
        raise Http404

    order.remove_item(item)
    return {'order': order}
