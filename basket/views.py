# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.template import loader
from django.conf import settings
from utils import render_to, send_mail, get_basket_from_request
from forms import BasketForm, BasketFormset
from models import Basket, BasketItem
from catalog.models import Item



@render_to('basket/basket.html')
def show_basket(request):
    basket = get_basket_from_request(request)
    if basket is None:
        return {'cookie_error': True}

    if request.method == 'POST':
        formset = BasketFormset(request.POST, instance=basket)
        if formset.is_valid():
            basket_items = formset.save()
            for basket_item in basket_items:
                basket.set_quantity(basket_item.item, basket_item.quantity)
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
    basket = request['basket']

    if request.method == 'POST':
        form = BasketForm(request.POST, instance=basket, user=request.user)
        if form.is_valid():
            basket = form.save(commit=False)
            if form.cleaned_data['use_discount']:
                if not request.user.is_anonymous():
                    try:
                        discount = request.user.get_profile().discount
                    except ObjectDoesNotExist:
                        discount = None
                else:
                    discount = None
            else:
                discount = None
            message = loader.render_to_string('basket/order.txt', {
                'basket': basket,
                'data': form.cleaned_data,
                'discount': discount,
            })
            send_mail(u'Форма заказа', message, [manager[1] for manager in settings.MANAGERS])
            basket.order()
            return HttpResponseRedirect(reverse('thankyou'))
    else:
        form = BasketForm(instance=basket, user=request.user)
    return {'form': form, 'basket': basket}

@render_to('basket/thankyou.html')
def thankyou(request):
    return {}

# ajax views

def add_to_basket(request):
    basket = request['basket']

    if 'item' in request.REQUEST:
        try:
            item_id = int(request.REQUEST.get('item'))
            item = Item.objects.get(id=item_id)
        except (Item.DoesNotExist, ValueError), e:
            return HttpResponseServerError(e)
        basket.add_item(item)
        return HttpResponse('OK')
    else:
        return HttpResponseServerError('Incorrect request')


def remove_from_basket(request):
    basket = request['basket']

    if 'item' in request.REQUEST:
        try:
            item_id = int(request.REQUEST.get('item'))
            item = Item.objects.get(id=item_id)
        except (Item.DoesNotExist, ValueError), e:
            return HttpResponseServerError(e)

        basket.remove_item(item)

@render_to('basket/basket_panel.html')
def ajax_basket(request):
    return {'basket': request['basket']}
