# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from catalog.models import Item
from django import forms
from datetime import datetime
from decimal import Decimal


class BasketManager(models.Manager):

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

            for basketitem in old_basket.basketitem_set.all():
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
    
    def order(self):
        self.order_date = datetime.now()
        self.save()
    
    def deliver(self):
        self.delivery_date = datetime.now()
        self.delivred = True
        self.save()

    def add_item(self, item):
        already_in_basket = self.basketitem_set.filter(item=item.id).count()
        
        if already_in_basket:
            basket_item = self.basketitem_set.get(item=item.id)
            basket_item.quantity = basket_item.quantity + 1
            basket_item.save()
        else:
            basket_item = BasketItem(item=item, quantity=1, basket=self)
            basket_item.save()
            self.basketitem_set.add(basket_item)
            self.save()

    def remove_item(self, item):
        basketitem = self.basketitem_set.get(item=item.id).delete()

    def set_quantity(self, item, quantity):
        already_in_basket = self.basketitem_set.filter(item=item.id).count()
        if quantity <= 0:
            if already_in_basket:
                self.remove_item(item)
            return

        if already_in_basket:
            basket_item = self.basketitem_set.get(item=item.id)
            basket_item.quantity = quantity
            basket_item.save()
        else:
            basket_item = BasketItem(item=item, quantity=quantity, basket=self)
            basket_item.save()
            self.basketitem_set.add(basket_item)
            self.save()
    
    def flush(self):
        for basket_item in self.basketitem_set.all():
            self.remove_item(basket_item.item)
    
    def calculate(self):
        total_goods = 0 
        total_price = Decimal('0.0')
        for basket_item in self.basketitem_set.all():
            total_price = total_price + (basket_item.item.price * basket_item.quantity)
            total_goods = total_goods + basket_item.quantity
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
        return 'basket %s' % self.basketitem_set.all()


class HiddenField(models.ForeignKey):
    def formfield(self, **kwargs):
        defaults = {'widget': forms.HiddenInput()}
        defaults.update(kwargs)
        return super(HiddenField, self).formfield(**defaults)

class BasketItem(models.Model):
    class Meta:
        ordering = ['item']

    basket = models.ForeignKey(Basket)
    item = HiddenField(Item)
    quantity = models.IntegerField(u'Количество')
