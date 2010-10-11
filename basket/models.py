# -*- coding: utf-8 -*-
from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils import simplejson
from django.contrib.admin.models import LogEntry
from datetime import datetime
from decimal import Decimal
from basket.settings import PRICE_ATTR, BASKET_ORDERINFO
from basket.utils import resolve_uid, import_item
from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import post_save

ACTION_CHOICES = (
        ('communication', 'Общение с клиентом'),
        ('forming', 'Формирование'),
        ('delivery', 'Доставка'),
        ('payment', 'Оплата'),
    )

STATE_CHOICES = (
        ('wait', 'Ожидание'),
        ('denied', 'Отказ'),
        ('confirm', 'Подтверждение заказа'),
        ('aligment', 'Согласование с клиентом'),
        ('formed', 'Сформирован'),
        ('intercity', 'Местная'),
        ('sent_with_courier', 'Отправлено курьером'),
        ('sent_in_company', 'Отправлено в транспортную компанию'),
        ('delivered', 'Доставлено'),
        ('full_payment', 'Полностью'),
        ('partially_payment', 'Частично'),
    )

ACTION_AND_STATE_CHOICES = {
    '':(('', '---------'),),
    'communication':(
        ('wait', 'Ожидание'),
        ('denied', 'Отказ'),
        ('confirm', 'Подтверждение заказа'),),
    'forming':(
        ('aligment', 'Согласование с клиентом'),
        ('formed', 'Сформирован'),),
    'delivery':(
        ('sent_with_courier', 'Отправлено курьером'),
        ('sent_in_company', 'Отправлено в транспортную компанию'),
        ('delivered', 'Доставлено'),
        ('denied', 'Отказ'),),
    'payment':(
        ('full_payment', 'Полностью'),
        ('partially_payment', 'Частично'),),
    }

DELIVER_TYPE = (
        ('undefined', 'Не установлен'),
        ('town', 'До города'),
        ('home', 'До дома'),
    )

class Status(models.Model):
    class Meta:
        verbose_name = u'Тип статуса'
        verbose_name_plural = u'Типы статуса'

    name = models.CharField(max_length=20, verbose_name=u'Название')
    closed = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

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
        order_info_class = get_order_info_class()
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
            except order_info_class.DoesNotExist:
                order_info_class.objects.create(order=order)
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
            ).order_by('-id')
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

    user = models.ForeignKey(User, verbose_name=u'Пользователь', null=True, blank=True)
    session = models.ForeignKey(Session, null=True, blank=True)
    form_data = models.TextField(verbose_name=u'Данные клиента', null=True)
    status = models.ForeignKey(Status, blank=True, null=True)

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

    def get_city(self):
        return self.orderinfo.city
    get_city.short_description = u'Город'

    def get_form_data(self):
        from basket.forms import OrderForm
        result = {}
        if self.form_data:
            for field_name, value in simplejson.loads(self.form_data).iteritems():
                result.update({
                    field_name: (value, OrderForm.base_fields[field_name].label),
                })
        return result

    def get_datetime(self):
        return self.orderinfo.registered.strftime("%d/%m/%y %H:%M")
    get_datetime.short_description = u'Зарегистрирован'

    def get_comment(self):
        states = self.states_set.all()
        if states:
            return states[0].comment
        return None
    get_comment.short_description = u'Примечание'

    def accepted(self):
        if self.states_set.filter(state='confirm'):
            return True
        else:
            return False
    accepted.short_description = u'Подт.'
    accepted.boolean = True

    def formed(self):
        if self.states_set.filter(state='formed'):
            return True
        else:
            return False
    formed.short_description = u'Сформ.'
    formed.boolean = True

    def paid(self):
        if self.states_set.filter(state='full_payment'):
            return True
        else:
            return False
    paid.short_description = u'Опл.'
    paid.boolean = True

    def get_phone(self):
        return self.orderinfo.telephone
    get_phone.short_description = u'Телефон'

    def __unicode__(self):
        return 'order #%s' % self.id

class OrderInfo(models.Model):
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

def get_order_info_class():
    try:
        order_info_class = import_item(BASKET_ORDERINFO, 'Can not import BASKET_ORDERINFO')
    except ImproperlyConfigured:
        return OrderInfo
    else:
        return order_info_class

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

class States(models.Model):
    order = models.ForeignKey(Order)
    action = models.CharField(choices=ACTION_CHOICES,
        verbose_name=u'Действие', max_length=100)
    state = models.CharField(choices=STATE_CHOICES,
        verbose_name=u'Состояние', max_length=100)
    comment = models.CharField(max_length=255, verbose_name=u'Комментарий',
        blank=True, null=True)
    modified = models.CharField(verbose_name=u'Изменен', max_length=100,
                                blank=True, null=True)

    class Meta:
        verbose_name = u'Действия с заказом'
        verbose_name_plural = u'Действия с заказом'

def get_status_types():
    '''Return chioces for status field'''
    return [(st.id, st.name) for st in Status.objects.all()]

def status_change(sender, instance, created, **kwargs):
    u'''Change status on some states'''
    state_change_status = {
        'denied': u'отказ',
        'delivered': u'завершён',
        'confirm': u'на обработке',
        }
    status_name = u'новый'
    states = instance.order.states_set.all()
    order = instance.order
    for state in states:
        if state.state in state_change_status:
            status_name = state_change_status[state.state]
            break
    if not order.status or status_name != order.status.name:
        status = Status.objects.get(name=status_name)
        order.status = status
        order.save()

post_save.connect(status_change, sender=States)
