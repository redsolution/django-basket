# encoding: utf-8
from basket.models import STATUS_NEW, STATUS_PROCESS, STATUS_CLOSED, \
    STATUS_ERROR, STATUS_PENDING
from django.template import loader
from south.db import db
from south.v2 import DataMigration
from django.utils import simplejson
import datetime


def comment_order(order):
    if order.form_data:
        cleaned_data = simplejson.loads(order.form_data)
        message = loader.render_to_string('basket/order.txt', {
            'order': order,
            'data': cleaned_data,
        })
        return message

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # copy session keys...
        for order in orm.Order.objects.filter(session__isnull=False):
            order.session_key = order.session_id
            order.save()
        # copy statuses...
        status_map = {
            u'новый': STATUS_NEW,
            u'оплачено': STATUS_PROCESS,
            u'отправлено': STATUS_CLOSED,
            u'ошибка': STATUS_ERROR
        }
        for order in orm.Order.objects.all():
            # get first order date
            if (order.orderstatus_set.all().count()):
                first_date = order.orderstatus_set.latest('date').date
                pending_date = first_date - datetime.timedelta(1)
            else:
                pending_date = datetime.datetime.now()

            # create status with form data
            orm.TempStatus.objects.create(
                order=order,
                status=STATUS_PENDING,
                modified=pending_date,
                comment=comment_order(order)
            )

            for order_status in order.orderstatus_set.all():
                status_data = {
                    'order': order,
                    'modified': order_status.date,
                    'comment': order_status.comment,
                }
                if order_status.type.name in status_map:
                    status_data['status'] = status_map[order_status.type.name]
                else:
                    status_data['status'] = STATUS_PROCESS
                    status_data['comment'] += u'Статус: %s' % order_status.type.name
                orm.TempStatus.objects.create(**status_data)


    def backwards(self, orm):
        "Write your backwards methods here."
        orm.TempStatus.objects.all().delete()
        print '"None shall pass!"'

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
            'form_data': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sessions.Session']", 'null': 'True', 'blank': 'True'}),
            'session_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'basket.orderstatus': {
            'Meta': {'object_name': 'OrderStatus'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 4, 6, 17, 34, 17, 331353)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['basket.Order']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['basket.Status']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'basket.status': {
            'Meta': {'object_name': 'Status'},
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'basket.tempstatus': {
            'Meta': {'object_name': 'TempStatus', 'db_table': "'basket_temp_status'"},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 4, 6, 17, 34, 17, 329071)'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['basket.Order']"}),
            'status': ('django.db.models.fields.IntegerField', [], {})
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
