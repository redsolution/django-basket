from basket.utils import get_basket_from_request


def user_basket(request):
    return {'basket': get_basket_from_request(request)}

