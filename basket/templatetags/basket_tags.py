from classytags.core import Tag, Options
from classytags.arguments import Argument
from classytags.helpers import InclusionTag
from django import template
from django.contrib.contenttypes.models import ContentType
from basket.models import *

register = template.Library()

class AddBasketButton(InclusionTag):
    name = 'add_basket_button'
    template = 'basket/button.html'
    
    options = Options(
        Argument('object', required=True, resolve=True),
        Argument('button_text', required=False, resolve=False),
        Argument('added_text', required=False, resolve=False),
        Argument('already_in_text', required=False, resolve=False),
        Argument('template_name', required=False, resolve=False),
    )

    def get_template(self, context, object, button_text, added_text, already_in_text, template_name):
        if template_name:
            template_to_render = template_name
        else:
            template_to_render = self.template
        return template_to_render
    
    def get_context(self, context, object, button_text, added_text, already_in_text, template_name):
        context_to_return = {}
        if object is None:
            context_to_return.update({
                'content_type': None,
                'object': None,
            })
        else:
            content_type = ContentType.objects.get_for_model(object)
            
            try:
                order_id = context['request'].session['order_id']
            
                # quantity of such items those are already into basket
                already_in_qty = BasketItem.objects.filter(order=order_id, content_type=content_type, object_id=object.id).count()
            
                # is any number of such items in the basket
                already_in = bool(already_in_qty)
            except KeyError:
                # for private mode
                already_in = False
                
            context_to_return.update({
                'content_type': content_type,
                'object': object,
                'button_text': button_text,
                'added_text': added_text,
                'already_in': already_in,
                'already_in_text': already_in_text,
            })
        return context_to_return

register.tag(AddBasketButton)

@register.filter
def content_type(object):
    '''
    returns content type id for object
    '''
    content_type = ContentType.objects.get_for_model(object)
    return '%s' % content_type.id
