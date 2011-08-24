import os
import django.core.mail
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db import models
from basket.settings import BASKET_FORM

def send_mail(subject, message, recipient_list):
    """
    Wrapper around standard Django ``send_mail``, converts `recipient_list`` into list
    and inserts DEFAULT_FROM_EMAIL as sender address
    """
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

def query_set_factory(model_name, query_set_class):
    '''
    Allows to create chained methods in model managers. For example: ::

        class UserQuerySet(models.query.QuerySet):

            def active(self):
                return self.filter(status=ACTIVE)


        class User(models.Model):
            status = models.IntegerField()
            objects = objects = query_set_factory('auth.User', UserQuerySet)

        >>> User.objects.filter(has_password=True).active()
    '''
    class ChainedManager(models.Manager):

        def get_query_set(self):
            model = models.get_model(*model_name.split('.'))
            return query_set_class(model)

        def __getattr__(self, attr, *args):
            try:
                return getattr(self.__class__, attr, *args)
            except AttributeError:
                return getattr(self.get_query_set(), attr, *args)
    return ChainedManager()
