import django.core.mail
from django.contrib.sites.models import Site
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from basket.models import Order


def get_order_from_request(request, create=False):
    # if we not request this variable, session wil not be created 
    session_key = request.session.session_key

    if request.user.is_authenticated():
        uid = request.user
    elif session_key:
        uid = session_key
    else:
        uid = None
    return Order.objects.get_order(uid, create)

def create_order_from_request(request):
    return get_order_from_request(request, True)

def send_mail(subject, message, recipent_list):
    from_email = settings.DEFAULT_FROM_EMAIL
    if type(recipent_list) is not list:
        recipent_list = [recipent_list, ]
    try:
        django.core.mail.send_mail(subject, message, from_email, recipent_list)
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

def import_item(path, error_text):
    """Imports a model by given string. In error case raises ImpoprelyConfigured"""
    i = path.rfind('.')
    module, attr = path[:i], path[i + 1:]
    try:
        return getattr(__import__(module, {}, {}, ['']), attr)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing %s %s: "%s"' % (error_text, path, e))
