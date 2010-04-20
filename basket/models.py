# -*- coding: utf-8 -*-
from django.db import models
from django import forms
from datetime import datetime
from decimal import Decimal
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from basket.settings import PRICE_ATTR
from basket.utils import resolve_uid
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session


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

    type = models.ForeignKey('Status')
    order = models.ForeignKey('Order')
    date = models.DateTimeField(default=lambda: datetime.now())
    comment = models.CharField(max_length=100, verbose_name=u'Комментарий',
        blank=True, null=True)

    def __unicode__(self):
        return self.type.name


class OrderManager(models.Manager):
    '''
    Custom manager for basket
    methods: 
        TODO: methods
    '''

    def from_uid(self, uid):
        '''
        Utility method, returns QuerySet of order objects 
        referenced to given uid: User id or session key
        
        Returns empty queryset if nothing found
        '''
        kwargs = resolve_uid(uid)
        if len(kwargs):
            return self.get_query_set().filter(**kwargs)
        else:
            return self.get_empty_query_set()

    def create_from_uid(self, uid):
        '''
        Returns new order referenced to given uid: user id or session key
        '''
        kwargs = resolve_uid(uid)
        if len(kwargs):
            return self.get_query_set().create(**kwargs)
        else:
            return self.get_empty_query_set()

    def get_order(self, uid, create=False):
        '''
            Get or create order, linked to given user or session.
            uid - User instance or session key (str)
        '''
        try:
            order = self.from_uid(uid).get(status__isnull=True)
        except Order.DoesNotExist:
            if create:
                order = self.create_from_uid(uid)
            else:
                order = None
        return order

    def get_last(self, uid):
        '''
        Return last order for given UID, supposed to be used after order confirmation:
        Notice: We should create order and redirect user, so he couldn't resend POST again.
                But order is already created at this moment, and request has no order attribute.
                So, I decided fetch last order from database with 'new' status   
        '''
        new_status = Status.objects.all()[0]
        last_queryset = self.from_uid(uid).filter(status=new_status
            ).order_by('-orderstatus__date')
        if last_queryset.count():
            return last_queryset[0]
        else:
            return None


    def history(self, uid):
        '''
        Returns closed orders of given user or session 
        '''
        return self.from_uid(uid).filter(status__closed=True)


class Order(models.Model):
    class Meta:
        verbose_name = u'Заказ'
        verbose_name_plural = u'Заказы'

    user = models.ForeignKey(User, verbose_name=u'Пользватель', null=True, blank=True)
    session = models.ForeignKey(Session, null=True, blank=True)
    status = models.ManyToManyField('Status', through='OrderStatus')

    objects = OrderManager()

    def registered(self):
        '''
        Returns True is order is from registered user
        '''
        if self.user is None:
            return False
        else:
            return True
    registered.short_description = u'Зарегистрирован'
    registered.boolean = True

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
                total_price += (basket_item.get_price() * basket_item.quantity)
            except AttributeError:
                pass
            total_goods += basket_item.quantity
        return {'goods': total_goods, 'price': total_price}

    def goods(self):
        return self.calculate()['goods']
    goods.short_description = u'Кол-во товаров'

    def price(self):
        return self.calculate()['price']
    price.short_description = u'Сумма'

    def empty(self):
        return self.goods() == 0

    def get_uid(self):
        if self.registered():
            return self.user
        else:
            return self.session

    def get_status(self):
        if self.orderstatus_set.count():
            return self.orderstatus_set.latest('date').type
        else:
            return u'Не оформлен'
    get_status.short_description = u'Статус заказа'

    def __unicode__(self):
        return 'order #%s' % self.id


class BasketItem(models.Model):
    class Meta:
        ordering = ['object_id']

    order = models.ForeignKey('Order', related_name='items')

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    quantity = models.IntegerField(u'Количество')

    def get_price(self):
        return getattr(self.content_object, PRICE_ATTR)

def get_status_types():
    '''Return chioces for status field'''
    return [(st.id, st.name) for st in Status.objects.all()]
