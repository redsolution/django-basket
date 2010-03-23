# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.template import loader
from basket.forms import OrderForm, OrderFormset
from basket.utils import render_to


@render_to('basket/basket.html')
def show_basket(request):
    order = request.order
    if order is None:
        return {'cookie_error': True}

    if request.method == 'POST':
        formset = OrderFormset(request.POST, instance=basket)
        if formset.is_valid():
            basket_items = formset.save()

            for basket_item in basket_items:
                basket.set_quantity(basket_item.content_object, basket_item.quantity)
            # remove items withuot checkboxes
            for form in formset.forms:
                keep = form.cleaned_data.get('keep', True)
                if not keep:
                    order.remove_item(form.instance.content_object)
            order.save()

            if 'ajax' in request.POST:
                # ajax basket update
                return {
                    'formset': OrderFormset(instance=basket),
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
    order = request.order

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=basket)
        if form.is_valid():
            order = form.save(commit=False)
            message = loader.render_to_string('basket/order.txt', {
                'order': order,
                'data': form.cleaned_data,
            })
            return HttpResponseRedirect(reverse('thankyou'))
    else:
        form = BasketForm(instance=basket)
    return {'form': form, 'basket': basket}

# ajax views

def add_to_basket(request):
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


def remove_from_basket(request):
    roder = request.order

    if 'item' in request.REQUEST:
        item_id = request.REQUEST.get('item', None)
        content_type_id, object_id = item_id.split('-')[1:]

        content_type = ContentType, obejcts.get(id=content_type_id)
        item = content_type.get_object_for_this_type(id=object_id)

        order.remove_item(item)
        return HttpResponse('OK')
    else:
        return HttpResponseServerError('Incorrect request')
