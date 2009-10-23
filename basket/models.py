# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django import forms
from datetime import datetime
from decimal import Decimal
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class BasketManager(models.Manager):
    '''
    Basket manager add extra methods to operate Basket models.

        get_basket - returns basket, connected to sessin or user
        history    - returns queryset with Basket obejcts, already ordered
        repeat     - creates new Basket object wich repeats old object
    '''
    def get_basket(self, uid):
        if type(uid) is str:
            try:
                session = Session.objects.get(pk=uid)
                (basket, created) = super(BasketManager, self
                    ).get_query_set().get_or_create(session=session,
                    order_date__isnull=True)
                if created:
                    basket.anonymous = True
                    basket.session = session
                    basket.save()
                return basket
            except Session.DoesNotExist:
                pass
        elif type(uid) is User:
            (basket, created) = super(BasketManager, self).get_query_set(
                ).get_or_create(user=uid, order_date__isnull=True)
            if created:
                basket.anonymous = False
                basket.user = uid
            return basket

    def history(self, uid):
        if type(uid) is str:
            try:
                session = Session.objects.get(pk=uid)
                history = super(BasketManager, self
                    ).get_query_set().filter(session=session, order_date__isnull=False
                    ).order_by('-order_date')
                return history
            except Session.DoesNotExist:
                pass
        elif type(uid) is User:
            history = super(BasketManager, self).get_query_set(
                ).filter(user=uid, order_date__isnull=False
                ).order_by('-order_date')
            return history
    
    def repeat(self, old_basket):
        if old_basket.user is not None:
            new_basket = self.get_basket(old_basket.user)
            new_basket.save()

            for basketitem in old_basket.items.all():
                new_basket.set_quantity(basketitem.item, basketitem.quantity)

            return new_basket


class Basket(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    session = models.ForeignKey(Session, null=True, blank=True)

    anonymous = models.BooleanField(u'Анонимный пользователь', default=True)
    
    order_date = models.DateTimeField(u'Дата заказа', null=True, blank=True)
    delivery_date = models.DateTimeField(u'Дата доставки', null=True, blank=True)
    delivered = models.BooleanField(u'Доставлено', null=True)

    objects = BasketManager()
    
    def order_now(self):
        self.order_date = datetime.now()
        self.save()
    
    def deliver_now(self):
        self.delivery_date = datetime.now()
        self.delivred = True
        self.save()

    def add_item(self, item):
        item_ct = ContentType.objects.get_for_model(item)
        already_in_basket = bool(
            self.items.filter(object_id=item.id, content_type=item_ct).count()
        )

        if already_in_basket:
            basket_item = self.items.get(object_id=item.id, content_type=item_ct)
            basket_item.quantity = basket_item.quantity + 1
            basket_item.save()
        else:
            basket_item = BasketItem(content_object=item, quantity=1, basket=self)
            basket_item.save()
            self.items.add(basket_item)
            self.save()

    def remove_item(self, item):
        item_ct = ContentType.objects.get_for_model(item)
        basketitem = self.items.filter(object_id=item.id, content_type=item_ct).delete()

    def set_quantity(self, item, quantity):
        item_ct = ContentType.objects.get_for_model(item)
        already_in_basket = bool(
            self.items.filter(object_id=item.id, content_type=item_ct).count()
        )
        if quantity <= 0:
            if already_in_basket:
                self.remove_item(item)
            return

        if already_in_basket:
            basket_item = self.items.get(object_id=item.id, content_type=item_ct)
            basket_item.quantity = quantity
            basket_item.save()
        else:
            basket_item = BasketItem(content_object=item, quantity=quantity, basket=self)
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
                total_price += (basket_item.content_object.price * basket_item.quantity)
            except AttributeError:
                pass
            total_goods += basket_item.quantity
        return {'goods': total_goods, 'price': total_price}
    
    def goods(self):
        return self.calculate()['goods']
    
    def price(self):
        return self.calculate()['price']
    
    def empty(self):
        return self.goods() == 0

    def get_uid(self):
        if self.anonymous:
            return self.session
        else:
            return self.user
    
    def __unicode__(self):
        return 'basket %s' % self.items.all()


class BasketItem(models.Model):
    class Meta:
        ordering = ['object_id']

    basket = models.ForeignKey(Basket, related_name='items')

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    quantity = models.IntegerField(u'Количество')

