from django import template
from django.contrib.contenttypes.models import ContentType
from basket.models import Order
from basket.utils import uid_from_request
from decimal import Decimal

register = template.Library()

@register.inclusion_tag('basket/history.html', takes_context=True)
def show_basket_history(context):
    """
    Show history.
    """
    request = context.get('request', None)
    if request:
        history = Order.objects.history(uid_from_request(request))
        last = Order.objects.get_last(uid_from_request(request))
        if history:
            history_sum = Decimal(sum([order.summary() for order in history]))
        else:
            history_sum = Decimal('0.00')
    return locals()

@register.inclusion_tag('basket/panel.html', takes_context=True)
def show_basket_panel(context):
    """
    Show basket panel.
    """
    return {}

@register.inclusion_tag('basket/button.html')
def add_basket_button(object):
    """
    Add button to add specified object to the basket.
    """
    content_type = ContentType.objects.get_for_model(object)
    return {'content_type': content_type, 'object': object, }
