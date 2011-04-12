# -*- coding: utf-8 -*-
from basket.models import Order
from basket.settings import BASKET_OPTIONS_USE_DELETE
from django.core.exceptions import ObjectDoesNotExist
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
import re

_BASKET_JS_RE = \
    re.compile(r'(<script\W[^>]*\bsrc\s*=\s*(\'|"|)[^\'^\"]*basket.js(\'|"|)\b[^>]*>\W*</\s*script\s*>)', re.IGNORECASE)
BASKET_URL_SCRIPT = '''
<script type="text/javascript">
basket.add_url = '%(add)s';
basket.del_url = '%(del)s';
</script>
'''

class BasketMiddleware(object):
    '''Add order attribute to request only if appropriate Order instance exists'''
    def process_request(self, request):
        if request.user.is_authenticated():
            if request.user.order_set.active_orders().count() == 1:
                request.order = request.user.order_set.active_orders().get()
                request.session['order_id'] = request.order.id
            elif request.user.order_set.active_orders().count() == 0:
                request.order = None
            else:
                # exception situation, two orders created!
                request.order = request.user.order_set.active_orders()[0]
                request.session['order_id'] = request.order.id
        else:
            if 'order_id' in request.session:
                try:
                    request.order = Order.objects.active_orders().get(
                        id=request.session['order_id'])
                except ObjectDoesNotExist:
                    # Order completed
                    del request.session['order_id']
                    request.order = None
            else:
                request.order = None

    def process_response(self, request, response):
        '''Add basket url to script'''
        urls = {
            'add': reverse('add_to_basket'),
        }
        if BASKET_OPTIONS_USE_DELETE:
            urls['del'] = reverse('del_from_basket')
        else:
            urls['del'] = ''
        try:
            def add_url_definition(match):
                return mark_safe(match.group() + BASKET_URL_SCRIPT % urls)
            response.content = _BASKET_JS_RE.sub(add_url_definition, response.content)
        except:
            return response
        else:
            return response
