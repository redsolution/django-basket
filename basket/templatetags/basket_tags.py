# -*- coding: utf-8 -*-
from classytags.arguments import Argument, ChoiceArgument
from classytags.core import Tag, Options
from django import template
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from basket.forms import AddItemForm

register = template.Library()

BUTTON_TYPE_SIMPLE = 'simple'
BUTTON_TYPE_AJAX = 'ajax'
BUTTON_TYPE_COUNTER = 'counter'
BUTTON_CHOICES = [BUTTON_TYPE_SIMPLE, BUTTON_TYPE_AJAX, BUTTON_TYPE_COUNTER]

class AddButton(Tag):
    '''
    Render add-to-basket button for generic object.
    
    **Usage**::
    
         {% add_basket_button object [type button_type] %}
    
    
    ``object`` - Django model instance, which you want to sell.
    ``button_type`` - type of button. Three types available now:
    
        - simple - after click user will be redirected to basket page (default argument),
        - ajax - adding to basket will not cause page reload,
        - counter - works the same as 'simple', but with quantity counter near submit button.
    
    **Examples**::
    
        {% add_basket_button item %}
    
    Displays ``simple`` button for item, which redirects to basket page.
    
        {% add_basket_button item type ajax %}
    
    Displays ajax button.
    '''
    name = 'add_basket_button'
    options = Options(
        Argument('instance'),
        'type',
        ChoiceArgument('button_type', resolve=False, required=False,
            default=BUTTON_TYPE_SIMPLE, choices=BUTTON_CHOICES),
    )
    templates = {
        BUTTON_TYPE_SIMPLE: 'basket/button/simple.html',
        BUTTON_TYPE_AJAX: 'basket/button/ajax.html',
        BUTTON_TYPE_COUNTER: 'basket/button/counter.html',
    }

    def render_tag(self, context, instance, button_type):
        return render_to_string(self.templates[button_type], {
            'form': AddItemForm.for_object(instance),
        })

register.tag(AddButton)
