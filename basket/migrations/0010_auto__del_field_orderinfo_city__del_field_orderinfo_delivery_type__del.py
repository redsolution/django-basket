# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'OrderInfo.city'
        db.delete_column('basket_orderinfo', 'city')

        # Deleting field 'OrderInfo.delivery_type'
        db.delete_column('basket_orderinfo', 'delivery_type')

        # Deleting field 'OrderInfo.delivery_datetime'
        db.delete_column('basket_orderinfo', 'delivery_datetime')

        # Deleting field 'OrderInfo.contact_time'
        db.delete_column('basket_orderinfo', 'contact_time')

        # Deleting field 'OrderInfo.discount'
        db.delete_column('basket_orderinfo', 'discount')

        # Deleting field 'OrderInfo.delivery_cost'
        db.delete_column('basket_orderinfo', 'delivery_cost')

        # Deleting field 'OrderInfo.trans_company'
        db.delete_column('basket_orderinfo', 'trans_company')

        # Deleting field 'OrderInfo.notify'
        db.delete_column('basket_orderinfo', 'notify')

        # Changing field 'OrderInfo.email'
        db.alter_column('basket_orderinfo', 'email', self.gf('django.db.models.fields.EmailField')(max_length=100, null=True))


    def backwards(self, orm):
        
        # Adding field 'OrderInfo.city'
        db.add_column('basket_orderinfo', 'city', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True), keep_default=False)

        # Adding field 'OrderInfo.delivery_type'
        db.add_column('basket_orderinfo', 'delivery_type', self.gf('django.db.models.fields.CharField')(default='undefined', max_length=100), keep_default=False)

        # Adding field 'OrderInfo.delivery_datetime'
        db.add_column('basket_orderinfo', 'delivery_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True), keep_default=False)

        # Adding field 'OrderInfo.contact_time'
        db.add_column('basket_orderinfo', 'contact_time', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True), keep_default=False)

        # Adding field 'OrderInfo.discount'
        db.add_column('basket_orderinfo', 'discount', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True), keep_default=False)

        # Adding field 'OrderInfo.delivery_cost'
        db.add_column('basket_orderinfo', 'delivery_cost', self.gf('django.db.models.fields.FloatField')(null=True, blank=True), keep_default=False)

        # Adding field 'OrderInfo.trans_company'
        db.add_column('basket_orderinfo', 'trans_company', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True), keep_default=False)

        # Adding field 'OrderInfo.notify'
        db.add_column('basket_orderinfo', 'notify', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Changing field 'OrderInfo.email'
        db.alter_column('basket_orderinfo', 'email', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'basket.basketitem': {
            'Meta': {'ordering': "['object_id']", 'object_name': 'BasketItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'null': 'True', 'to': "orm['basket.Order']"}),
            'quantity': ('django.db.models.fields.IntegerField', [], {})
        },
        'basket.order': {
            'Meta': {'object_name': 'Order'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sessions.Session']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['basket.Status']", 'through': "'OrderStatus'"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'basket.orderinfo': {
            'Meta': {'object_name': 'OrderInfo'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'fio': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['basket.Order']", 'unique': 'True'}),
            'registered': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'basket.orderstatus': {
            'Meta': {'ordering': "['date']", 'object_name': 'OrderStatus'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 11, 26, 14, 51, 25, 582000)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['basket.Order']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['basket.Status']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'basket.status': {
            'Meta': {'object_name': 'Status'},
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'sessions.session': {
            'Meta': {'object_name': 'Session', 'db_table': "'django_session'"},
            'expire_date': ('django.db.models.fields.DateTimeField', [], {}),
            'session_data': ('django.db.models.fields.TextField', [], {}),
            'session_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'})
        }
    }

    complete_apps = ['basket']
