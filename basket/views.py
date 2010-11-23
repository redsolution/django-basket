# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from basket.forms import OrderForm, OrderFormset, OrderStatusForm
from basket.utils import render_to, get_order_from_request, create_order_from_request, uid_from_request
from basket.models import Status, OrderStatus, Order
from basket.forms import get_order_form


@render_to('basket/basket.html')
def show_basket(request):
    # do not create order automatically
    order = request.order
    # there are four places where we check that basket is not empty
    # otherwise, return page with empty basket message
    # in order to avoid to show basket with 0 goods
    # 1st place
    if order is None or order.empty():
        return {}

    if request.method == 'POST':
        formset = OrderFormset(request.POST, instance=order)

        # empty basket condition
        # 2nd place
        if len(formset.forms) == 0:
            return {}

        if formset.is_valid():
            basket_items = formset.save()

            for basket_item in basket_items:
                order.set_quantity(basket_item.content_object, basket_item.quantity)
            # remove items withuot checkboxes
            for form in formset.forms:
                keep = form.cleaned_data.get('keep', True)
                if not keep:
                    order.remove_item(form.instance.content_object)
            order.save()

            # 3rd place
            if order.empty():
                return {}

            if 'ajax' in request.POST:
                # ajax basket update
                formset = OrderFormset(instance=order)
                # empty basket condition
                # and 4th place
                if len(formset.forms) == 0:
                    return {}
                else:
                    return {
                        'formset': formset,
                        'order': order
                    }
            else:
                return HttpResponseRedirect(reverse('confirm'))

    else:
        formset = OrderFormset(instance=order)

    return {
        'formset': formset,
        'order': order,
    }

@render_to('basket/confirm.html')
def confirm(request):
    # do not create order automatically
    order = request.order
    orderinfo = order.orderinfo

    if order:
        if request.method == 'POST':
            form = get_order_form()(request.POST, instance=orderinfo)
            if form.is_valid():
                form.save()
                first_status = Status.objects.all()[0]
                OrderStatus.objects.create(order=order, type=first_status,
                    comment=u'Онлайн заказ')
                return HttpResponseRedirect(reverse('thankyou'))
        else:
            form = get_order_form()(instance=orderinfo)
        return {'form': form, 'order': order}

@render_to('basket/thankyou.html')
def thankyou(request):
    order = Order.objects.get_last(uid_from_request(request))
    return {'order': order}

@render_to('basket/order_status.html')
def order_status(request):
    if request.method == 'POST':
        form = OrderStatusForm(request.POST)
        if form.is_valid():
            try:
                order = Order.objects.get(id=form.cleaned_data['order_id'])
                return {
                    'status': order.get_status(),
                    'history': order.orderstatus_set.all(),
                }
            except Order.DoesNotExist:
                return {
                    'form': form,
                    'order_id': form.cleaned_data['order_id']
                }
        else:
            return {'form': form}
    else:
        return {'form': OrderStatusForm()}


# ajax views

def add_to_basket(request):
    if request.order is None:
        order = create_order_from_request(request)
    else:
        order = request.order

    if 'item' in request.REQUEST:
        item_id = request.REQUEST.get('item', None)
        content_type_id, object_id = item_id.split('-')[1:]

        content_type = ContentType.objects.get(id=content_type_id)
        item = content_type.get_object_for_this_type(id=object_id)

        order.add_item(item)
        return HttpResponse('OK')
    else:
        return HttpResponseServerError('Incorrect request')
