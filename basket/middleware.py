from basket.models import Order
from basket.utils import get_order_from_request
from django.core.exceptions import ObjectDoesNotExist


class BasketMiddleware(object):
    '''Add basket attribute to request'''
    def process_request(self, request):
        # TODO:
#        if user.is_authenicated():
#            try to get user order from DB, with manager method, for example, active()
#            if order if found:
#                request.order = order
#            else:
#                pass
#        else:
#            if 'order_id' in request.session:
#                try:
#                    request.order = Order.objects.active().get(id=request.session['order_id'])
#                except DoesNotExist:
#                    pass
#            else:
#                pass
            