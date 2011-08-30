# -*- coding: utf-8 -*-
from basket.settings import PRICE_ATTR
from basket.utils import query_set_factory
from datetime import datetime
from decimal import Decimal
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
import warnings


STATUS_PENDING = 0
STATUS_NEW = 1
STATUS_PROCESS = 2
STATUS_CLOSED = 3
STATUS_ERROR = 4

STATUS_CHIOCES = (
    (STATUS_PENDING, _('Pending')),
    (STATUS_NEW, _('New')),
    (STATUS_PROCESS, _('Process')),
    (STATUS_CLOSED, _('Closed & OK')),
    (STATUS_ERROR, _('Closed with error')),
)


class OrderQuerySet(models.query.QuerySet):

    def active_orders(self):
        '''Filters active orders, which can be changed by user'''
        return self.filter(status=STATUS_PENDING)


class Order(models.Model):
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    user = models.ForeignKey(User, verbose_name=_('User'), null=True, blank=True)
    session_key = models.CharField(verbose_name=_('Session key'),
        max_length=40, null=True, blank=True)
    # fields from order status
    status = models.IntegerField(verbose_name=_('Order status'), choices=STATUS_CHIOCES)
    created = models.DateTimeField(verbose_name=_('Created date'))
    comment = models.TextField(verbose_name=_('Comment'), blank=True, null=True)

    objects = query_set_factory('basket.Order', OrderQuerySet)

    def registered(self):
        '''
        Returns True is order is from registered user
        '''
        if self.user is None:
            return False
        else:
            return True
    registered.short_description = _('Registered user')
    registered.boolean = True

    @classmethod
    def from_request(cls, request):
        '''
        Utility for creating orders from HttpRequest instances.
        Takes into account authorized users and anonymous.
        Example: ::
        
            def add_to_basket(request):
                # Automatically create order if it does not exist
                if request.order is None:
                    order = Order.from_request(request)
                    request.order = order
                    ...
        '''
        order = cls()
        if request.user.is_authenticated():
            order.user = request.user
        else:
            order.session_key = request.session.session_key
        order.status = STATUS_PENDING
        order.created = datetime.now()
        order.save()
        request.session['order_id'] = order.id
        return order

    def add_item(self, item, quantity=1, item_ct=None):
        '''
        Alias for ``set_quantity`` with one difference:
        ``quantity`` argument has default value 1. 
        '''
        self.set_quantity(item, quantity, item_ct=None)

    def remove_item(self, item, item_ct=None):
        '''
        Alias for ``set_quantity``. Specifies ``quantity`` = 0
        '''
        self.set_quantity(item, 0, item_ct)

    def set_quantity(self, item, quantity, item_ct=None):
        '''
        Puts item in a basket.
        Arguments: 
        
        - ``item`` - any Django model instance
        - ``qty`` - quantity of item. If 0 specified, deletes this item
            (if there were any before adding) from basket.
        - ``item_ct`` - precalculated ContentType for item. If not specified, 
            it will automatically calculated
        '''
        if item_ct is None:
            item_ct = ContentType.objects.get_for_model(item)

        already_in_order = bool(
            self.items.filter(object_id=item.id, content_type=item_ct).count()
        )

        if quantity <= 0:
            if already_in_order:
                self.remove_item(item)
            return

        if already_in_order:
            basket_item = self.items.get(object_id=item.id, content_type=item_ct)
            basket_item.quantity = quantity
            basket_item.save()
        else:
            basket_item = BasketItem(content_object=item, quantity=quantity, order=self)
            basket_item.save()
            self.items.add(basket_item)
            self.save()

    def flush(self):
        '''
        Deletes all items from order.
        '''
        for basket_item in self.items.all():
            basket_item.delete()

    @property
    def total(self):
        '''
        Total property returns dictoinary with total item count in order and 
        total price. For example:::
            
            >>> order.total
            {'count': 10, 'price': Decimal('110.1')}
        
        '''
        total_goods = 0
        total_price = Decimal('0.0')
        for basket_item in self.items.all():
            try:
                total_price += basket_item.get_sum()
            except AttributeError:
                pass
            total_goods += basket_item.quantity
        return {'count': total_goods, 'price': total_price}

    def goods(self):
        '''
        Deprecated. Use ``order.total['count']`` instead of ``order.goods()``
        '''
        warnings.warn(
            "Use order.total['count'] instead of order.goods()",
            DeprecationWarning
        )
        return self.total()['count']
    goods.short_description = _('Total items in basket')

    def summary(self):
        '''
        Deprecated. Use ``order.total['price']`` instead of ``order.summary()``
        '''
        warnings.warn(
            "Use order.total['price'] instead of order.summary()",
            DeprecationWarning
        )
        return self.total()['price']
    summary.short_description = _('Total price')

    def get_status(self):
        '''
        Returns latest changed order status. Used in admin interface.
        '''
        return self.status_set.latest('modified')
    get_status.short_description = _('Order status')

    @property
    def empty(self):
        return self.goods() == 0

    def __unicode__(self):
        return 'order #%s' % self.id


class BasketItem(models.Model):
    class Meta:
        ordering = ['object_id']

    order = models.ForeignKey('Order', related_name='items', null=True, blank=False)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    quantity = models.IntegerField(verbose_name=_('Quantity'))

    def get_price(self):
        '''
        Returns price accordind to PRICE_ATTR setting.
        The order of retrieving price value:
        1. Lambda-method lookup:::
        
            value = PRICE_ATTR(self.content_object)
        
        2. Attribute lookup::
        
            value = getattr(self.content_object, PRICE_ATTR)
        
        Callable result supported:::
            
            >> value = PRICE_ATTR(self.content_object)  # apply lambda-method for object
            >> value = value()  # execute result again
        '''
        if callable(PRICE_ATTR):
            value = PRICE_ATTR(self.content_object)
        else:
            value = getattr(self.content_object, PRICE_ATTR)
        if callable(value):
            value = value()
        return value

    def get_sum(self):
        return self.get_price() * self.quantity
