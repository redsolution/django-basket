from basket.utils import create_order_from_request


class BasketMiddleware(object):
    '''Add basket attribute to request'''
    def process_request(self, request):
        setattr(request, 'order', create_order_from_request(request))
