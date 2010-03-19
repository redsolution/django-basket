from basket.utils import get_basket_from_request


class BasketMiddleware(object):
    '''Add basket attribute to request'''
    def process_request(self, request):
        setattr(request, 'basket', get_basket_from_request(request))
