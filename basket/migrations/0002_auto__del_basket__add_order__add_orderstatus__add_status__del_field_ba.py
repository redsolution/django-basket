# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Deleting model 'Basket'
        db.delete_table('basket_basket')

        # Adding model 'Order'
        db.create_table('basket_order', (
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sessions.Session'], null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
        ))
        db.send_create_signal('basket', ['Order'])

        # Adding model 'OrderStatus'
        db.create_table('basket_orderstatus', (
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now())),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['basket.Status'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['basket.Order'])),
        ))
        db.send_create_signal('basket', ['OrderStatus'])

        # Adding model 'Status'
        db.create_table('basket_status', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('closed', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('basket', ['Status'])

        # Deleting field 'BasketItem.basket'
        db.delete_column('basket_basketitem', 'basket_id')

        # Deleting field 'BasketItem.item'
        db.delete_column('basket_basketitem', 'item_id')

        # Adding field 'BasketItem.object_id'
        db.add_column('basket_basketitem', 'object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True))

        # Adding field 'BasketItem.content_type'
        db.add_column('basket_basketitem', 'content_type', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['contenttypes.ContentType']), keep_default=False)

        # Adding field 'BasketItem.order'
        db.add_column('basket_basketitem', 'order', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', null=True, to=orm['basket.Order']), keep_default=False)


    def backwards(self, orm):

        # Adding model 'Basket'
        db.create_table('basket_basket', (
            ('delivered', self.gf('django.db.models.fields.BooleanField')(null=True, blank=True)),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sessions.Session'], null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('anonymous', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('order_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('delivery_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('basket', ['Basket'])

        # Deleting model 'Order'
        db.delete_table('basket_order')

        # Deleting model 'OrderStatus'
        db.delete_table('basket_orderstatus')

        # Deleting model 'Status'
        db.delete_table('basket_status')

        # Adding field 'BasketItem.basket'
        db.add_column('basket_basketitem', 'basket', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['basket.Basket']), keep_default=False)

        # Adding field 'BasketItem.item'
        db.add_column('basket_basketitem', 'item', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['custom_catalog.Item']), keep_default=False)

        # Deleting field 'BasketItem.object_id'
        db.delete_column('basket_basketitem', 'object_id')

        # Deleting field 'BasketItem.content_type'
        db.delete_column('basket_basketitem', 'content_type_id')

        # Deleting field 'BasketItem.order'
        db.delete_column('basket_basketitem', 'order_id')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'basket.basketitem': {
            'Meta': {'object_name': 'BasketItem'},
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
        'basket.orderstatus': {
            'Meta': {'object_name': 'OrderStatus'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now()'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['basket.Order']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['basket.Status']"})
        },
        'basket.status': {
            'Meta': {'object_name': 'Status'},
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
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
