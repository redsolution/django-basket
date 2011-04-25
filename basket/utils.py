import os
import django.core.mail
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from basket.settings import BASKET_FORM

def send_mail(subject, message, recipient_list):
    from_email = settings.DEFAULT_FROM_EMAIL
    if type(recipient_list) is not list:
        recipient_list = [recipient_list, ]
    try:
        django.core.mail.send_mail(subject, message, from_email, recipient_list)
    except Exception, e:
        print 'Error while sending mail: ', e

def render_to(template_path):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            output = func(request, *args, **kwargs)
            if output is None:
                output = {}
            if not isinstance(output, dict):
                return output
            return render_to_response(template_path, output,
                context_instance=RequestContext(request))
        return wrapper
    return decorator

def import_item(path, error_text=''):
    """Imports a model by given string. In error case raises ImpoprelyConfigured"""
    i = path.rfind('.')
    module, attr = path[:i], path[i + 1:]
    try:
        return getattr(__import__(module, {}, {}, ['']), attr)
    except ImportError, e:
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured('Error importing %s %s: "%s"' % (error_text, path, e))

def get_order_form():
    return import_item(BASKET_FORM)
