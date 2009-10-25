# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.template import loader
from django.conf import settings
from basket.forms import BasketForm, BasketFormset
from basket.utils import render_to, send_mail, get_basket_from_request
from basket.models import Basket, BasketItem


@render_to('basket/basket.html')
def show_basket(request):
    basket = request.basket
    if basket is None:
        return {'cookie_error': True}

    if request.method == 'POST':
        formset = BasketFormset(request.POST, instance=basket)
        if formset.is_valid():
            basket_items = formset.save()

            for basket_item in basket_items:
                basket.set_quantity(basket_item.content_object, basket_item.quantity)
            # remove items withuot checkboxes
            for form in formset.forms:
                keep = form.cleaned_data.get('keep', True)
                if not keep:
                    basket.remove_item(form.instance.content_object)
            basket.save()
            
            if 'ajax' in request.POST:
                return {'formset': BasketFormset(instance=basket),
                        'basket': basket}
            else:
                return HttpResponseRedirect(reverse('confirm'))
    else:
        formset = BasketFormset(instance=basket)

    return {'formset': formset,
            'basket': basket}

@render_to('basket/confirm.html')
def confirm(request):
    basket = request.basket

    if request.method == 'POST':
        form = BasketForm(request.POST, instance=basket)
        if form.is_valid():
            basket = form.save(commit=False)
            message = loader.render_to_string('basket/order.txt', {
                'basket': basket,
                'data': form.cleaned_data,
            })
            send_mail(u'Форма заказа', message, [manager[1] for manager in settings.MANAGERS])
            basket.order_now()
            return HttpResponseRedirect(reverse('thankyou'))
    else:
        form = BasketForm(instance=basket)
    return {'form': form, 'basket': basket}

# ajax views

def add_to_basket(request):
    basket = request.basket

    if 'item' in request.REQUEST:
        item_id = request.REQUEST.get('item', None)
        content_type_id, object_id = item_id.split('-')[1:]

        content_type = ContentType.objects.get(id=content_type_id)
        item = content_type.get_object_for_this_type(id=object_id)

        basket.add_item(item)
        return HttpResponse('OK')
    else:
        return HttpResponseServerError('Incorrect request')


def remove_from_basket(request):
    basket = request.basket

    if 'item' in request.REQUEST:
        item_id = request.REQUEST.get('item', None)
        content_type_id, object_id = item_id.split('-')[1:]

        content_type = ContentType,obejcts.get(id=content_type_id)
        item = content_type.get_object_for_this_type(id=object_id)

        basket.remove_item(item)
        return HttpResponse('OK')
    else:
        return HttpResponseServerError('Incorrect request')

