from django import template
from django.contrib.contenttypes.models import ContentType

register = template.Library()

@register.inclusion_tag('basket/button.html')
def add_basket_button(object):
    """
    Add button to add specified object to the basket.
    """
    if object is None:
        return {'content_type': None, 'object': None, }
    content_type = ContentType.objects.get_for_model(object)
    return {'content_type': content_type, 'object': object, }

@register.filter
def content_type(object):
    '''
    returns content type id for object
    '''
    content_type = ContentType.objects.get_for_model(object)
    return '%s' % content_type.id
