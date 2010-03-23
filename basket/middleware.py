from basket.utils import get_order_from_request


class BasketMiddleware(object):
    '''Add basket attribute to request'''
    def process_request(self, request):
        setattr(request, 'order', get_order_from_request(request))
