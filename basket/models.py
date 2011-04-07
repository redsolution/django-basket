# -*- coding: utf-8 -*-
from basket.settings import PRICE_ATTR
from datetime import datetime
from decimal import Decimal
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from django.db.models import Count
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

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

def query_set_factory(model_name, query_set_class):
    class ChainedManager(models.Manager):

        def get_query_set(self):
            model = models.get_model('basket', model_name)
            return query_set_class(model)

        def __getattr__(self, attr, *args):
            try:
                return getattr(self.__class__, attr, *args)
            except AttributeError:
                return getattr(self.get_query_set(), attr, *args)
    return ChainedManager()

class TempStatus(models.Model):
    class Meta:
        verbose_name = _('Order status')
        verbose_name_plural = _('Order statuses')
        ordering = ['modified']
        db_table = 'basket_temp_status'

    status = models.IntegerField(verbose_name=_('Order status'), choices=STATUS_CHIOCES)
    order = models.ForeignKey('Order')

    modified = models.DateTimeField(default=lambda: datetime.now(),
        verbose_name=_('Last modified date'))
    comment = models.CharField(max_length=500, verbose_name=_('Comment'),
        blank=True, null=True)

class Status(models.Model):
    class Meta:
        verbose_name = u'Тип статуса'
        verbose_name_plural = u'Типы статуса'

    name = models.CharField(max_length=20, verbose_name=u'Название')
    closed = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class OrderStatus(models.Model):
    class Meta:
        verbose_name = u'Статус заказа'
        verbose_name_plural = u'Статусы заказа'
        ordering = ['date']

    type = models.ForeignKey('Status', verbose_name=u'Тип статуса')
    order = models.ForeignKey('Order')
    date = models.DateTimeField(default=lambda: datetime.now(), verbose_name=u'Дата')
    comment = models.CharField(max_length=100, verbose_name=u'Комментарий',
        blank=True, null=True)
    user = models.ForeignKey('auth.User', verbose_name=u'Пользователь', null=True, blank=True)

    def __unicode__(self):
        return self.type.name

    def __unicode__(self):
        return 'Order #%d status' % (self.order.id)


class OrderQuerySet(models.query.QuerySet):

    def active_orders(self):
        '''Filters active orders, which can be changed by user'''
        return self.annotate(num_statuses=Count('status')).filter(
            num_statuses=1).filter(status__status=STATUS_PENDING)


class Order(models.Model):
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    user = models.ForeignKey(User, verbose_name=_('User'), null=True, blank=True)
    session = models.ForeignKey(Session, null=True, blank=True)
    session_key = models.CharField(verbose_name=_('Session key'),
        max_length=40, null=True, blank=True)
    form_data = models.TextField(verbose_name=u'Данные клиента', null=True)

    objects = query_set_factory('Order', OrderQuerySet)

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
        order = cls()
        if request.user.is_authenticated():
            order.user = request.user
        else:
            order.session_key = request.session.session_key
        order.save()
        comment = ugettext('Automatically created status')
        Status.objects.create(status=STATUS_PENDING, order=order,
            comment=comment)
        request.session['order_id'] = order.id
        return order

    def add_item(self, item):
        item_ct = ContentType.objects.get_for_model(item)
        already_in_order = bool(
            self.items.filter(object_id=item.id, content_type=item_ct).count()
        )

        if already_in_order:
            basket_item = self.items.get(object_id=item.id, content_type=item_ct)
            basket_item.quantity += 1
            basket_item.save()
        else:
            basket_item = BasketItem(content_object=item, quantity=1, order=self)
            basket_item.save()
            self.items.add(basket_item)
            self.save()

    def remove_item(self, item):
        item_ct = ContentType.objects.get_for_model(item)
        self.items.filter(object_id=item.id, content_type=item_ct).delete()

    def set_quantity(self, item, quantity):
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
        for basket_item in self.items.all():
            basket_item.delete()

    def calculate(self):
        total_goods = 0
        total_price = Decimal('0.0')
        for basket_item in self.items.all():
            try:
                total_price += basket_item.get_sum()
            except AttributeError:
                pass
            total_goods += basket_item.quantity
        return {'goods': total_goods, 'summary': total_price}

    def goods(self):
        return self.calculate()['goods']
    goods.short_description = _('Total items in basket')

    def summary(self):
        return self.calculate()['summary']
    summary.short_description = _('Total price')

    def get_status(self):
        return self.status_set.latest('modified')
    get_status.short_description = _('Order status')

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
        if callable(PRICE_ATTR):
            value = PRICE_ATTR(self.content_object)
        else:
            value = getattr(self.content_object, PRICE_ATTR)
        if callable(value):
            value = value()
        return value

    def get_sum(self):
        return self.get_price() * self.quantity

