# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from datetime import datetime
from decimal import Decimal
from basket.settings import PRICE_ATTR, BASKET_MODEL
from basket.utils import resolve_uid, import_item, BogusSMTPConnection

DELIVER_TYPE = (
        ('undefined', 'Не установлен'),
        ('town', 'До города'),
        ('home', 'До дома'),
    )

class StatusManager(models.Manager):
    def get_default(self):
        try:
            return self.get_query_set().get(default=True)
        except ObjectDoesNotExist:
            return self.get_query_set().create(name=u'Новый заказ', default=True, closed=False)


class Status(models.Model):
    class Meta:
        verbose_name = u'Тип статуса'
        verbose_name_plural = u'Типы статуса'

    name = models.CharField(max_length=20, verbose_name=u'Название')
    default = models.BooleanField(verbose_name=u'Используется по умолчанию', default=False)
    closed = models.BooleanField(verbose_name=u'Заказ выполнен', default=False)
    
    objects = StatusManager()
    
    def save(self, *args, **kwargs):
        super(Status, self).save(*args, **kwargs)
        if self.default:
            for status in Status.objects.filter(default=True).exclude(id=self.id):
                status.default=False
                status.save()

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
        
        Returns None if uid is not valid.
        '''
        kwargs = resolve_uid(uid)
        if len(kwargs):
            return self.get_query_set().create(**kwargs)
        else:
            return None

    def get_order(self, uid, create=False):
        '''
            Get or create order, linked to given user or session.
            uid - User instance or session key (str)
        '''
        order_model = get_order_model()
        try:
            order = self.from_uid(uid).get(status__isnull=True)
        except Order.DoesNotExist:
            if create:
                order = self.create_from_uid(uid)
            else:
                order = None
        if order:
            try:
                order.orderinfo
            except ObjectDoesNotExist:
                order_model.objects.create(order=order)
        return order

    def get_last(self, uid):
        '''
        Return last order for given UID, supposed to be used after order confirmation:
        Notice: We should create order and redirect user, so he couldn't resend POST again.
                But order is already created at this moment, and request has no order attribute.
                So, I decided fetch last order from database with 'new' status   
        '''
        last_queryset = self.from_uid(uid).filter(status=Status.objects.get_default()
            ).order_by('-orderstatus__date')
        if last_queryset.count():
            return last_queryset[0]
        else:
            return None


    def closed(self, uid):
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
                total_price += basket_item.get_sum()
            except AttributeError:
                pass
            total_goods += basket_item.quantity
        return {'goods': total_goods, 'summary': total_price}

    def goods(self):
        return self.calculate()['goods']
    goods.short_description = u'Кол-во товаров'

    def summary(self):
        return self.calculate()['summary']
    summary.short_description = u'Сумма'

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
            return Status.objects.get_default()
    get_status.short_description = u'Статус заказа'

    def __unicode__(self):
        return 'order #%s' % self.id

class OrderInfo(models.Model):
    '''
    Order information model. If you want to override default fields, set BASKET_MODEL in settings.py.
    For more information check default settings in basket/settings.py
    '''
    order = models.OneToOneField(Order)
    registered = models.DateTimeField(verbose_name=u'Дата и время поступления', auto_now_add=True)
    fio = models.CharField(verbose_name=u'ФИО', max_length=100, blank=True,
                           null=True)
    email = models.CharField(verbose_name=u'e-mail', max_length=100, blank=True,
                             null=True)
    telephone = models.CharField(verbose_name=u'Телефон', max_length=100,
                                 blank=True, null=True)
    city = models.CharField(verbose_name=u'Город', max_length=100,
                            blank=True, null=True)
    address = models.CharField(verbose_name=u'Адрес доставки', max_length=100,
                              blank=True, null=True)
    contact_time = models.CharField(verbose_name=u'Удобное время для связи',
            max_length=100, blank=True, null=True)
    discount = models.IntegerField(verbose_name=u'Накопленная скидка',
                                   blank=True, null=True)
    trans_company = models.CharField(verbose_name=u'Транспортная компания',
        max_length=10, blank=True, null=True)
    delivery_type = models.CharField(choices=DELIVER_TYPE, verbose_name=u'Тип доставки',
        max_length=100, default='undefined')
    delivery_cost = models.FloatField(verbose_name=u'Cтоимость доставки',
            blank=True, null=True)
    delivery_datetime = models.DateTimeField(verbose_name=u'Дата и время доставки',
            blank=True, null=True)
    notify = models.BooleanField(verbose_name=u'Оповестить перед доставкой', default=False)
    comment = models.CharField(verbose_name=u'Комментарий', max_length=200,
        blank=True, null=True)

    class Meta:
        verbose_name = u'Параметры заказа'
        verbose_name_plural = u'Параметры заказа'

def get_order_model():
    try:
        order_model = import_item(BASKET_MODEL, 'Can not import BASKET_MODEL')
    except ImproperlyConfigured:
        return OrderInfo
    else:
        return order_model

class BasketItem(models.Model):
    class Meta:
        ordering = ['object_id']

    order = models.ForeignKey('Order', related_name='items', null=True, blank=False)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    quantity = models.IntegerField(u'Количество')

    def get_price(self):
        return getattr(self.content_object, PRICE_ATTR)

    def get_sum(self):
        return self.get_price() * self.quantity

if settings.DEBUG:
    from django.core import mail
    mail.SMTPConnection = BogusSMTPConnection
