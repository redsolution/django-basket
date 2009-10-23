from django import template
from catalog.models import Section, TreeItem
from basket.views import get_basket_from_request
from basket.models import Basket
from decimal import Decimal

register = template.Library()


@register.inclusion_tag('basket/basket_history.html', takes_context=True)
def show_basket_history(context):
    request = context.get('request', None)
    if request is not None:
        history = Basket.objects.history(request.user)
        if history:
            history_sum = int(sum([basket.price() for basket in history]))
        else:
            history_sum = Decimal('0.00')
    return locals()

