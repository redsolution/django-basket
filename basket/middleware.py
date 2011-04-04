from basket.models import Order
from django.core.exceptions import ObjectDoesNotExist


class BasketMiddleware(object):
    '''Add order attribute to request only if appropriate Order instance exists'''
    def process_request(self, request):
        if request.user.is_authenticated():
            if request.user.order_set.new_orders().count() == 1:
                request.order = request.user.order_set.new_orders().get()
                request.session['order_id'] = request.order.id
            elif request.user.order_set.new_orders().count() == 0:
                pass
            else:
                # exception situation, two orders created!
                request.order = request.user.order_set.new_orders()[0]
                request.session['order_id'] = request.order.id
        else:
            if 'order_id' in request.session:
                try:
                    request.order = Order.objects.new_orders().get(
                        id=request.session['order_id'])
                except ObjectDoesNotExist:
                    # Order completed
                    del request.session['order_id']
            