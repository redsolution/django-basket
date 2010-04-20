from django import template
from django.contrib.contenttypes.models import ContentType
from basket.models import Order
from basket.utils import uid_from_request
from decimal import Decimal

register = template.Library()


@register.inclusion_tag('basket/basket_history.html', takes_context=True)
def show_basket_history(context):
    request = context.get('request', None)
    if request:
        history = Order.objects.history(uid_from_request(request))
        last = Order.objects.get_last(uid_from_request(request))
        if history:
            history_sum = Decimal(sum([order.price() for order in history]))
        else:
            history_sum = Decimal('0.00')
    return locals()

@register.simple_tag
def basket_add(item):
    ct = ContentType.objects.get_for_model(item)
    return 'item-%s-%s' % (ct.id, item.id)
