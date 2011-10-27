# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Account'
        db.create_table('transactions_account', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['foundations.Currency'])),
            ('start_balance', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=2)),
        ))
        db.send_create_signal('transactions', ['Account'])

        # Adding M2M table for field owner on 'Account'
        db.create_table('transactions_account_owner', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('account', models.ForeignKey(orm['transactions.account'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('transactions_account_owner', ['account_id', 'user_id'])

        # Adding model 'Transaction'
        db.create_table('transactions_transaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('original_description', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True)),
        ))
        db.send_create_signal('transactions', ['Transaction'])

        # Adding model 'TransactionAssignment'
        db.create_table('transactions_transactionassignment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('transaction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['transactions.Transaction'])),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['transactions.Account'], null=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=2)),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['foundations.Currency'], null=True, blank=True)),
            ('is_reconciled', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('transactions', ['TransactionAssignment'])

        # Adding model 'Category'
        db.create_table('transactions_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['auth.User'])),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['transactions.Category'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('transactions', ['Category'])

        # Adding model 'TransactionCategory'
        db.create_table('transactions_transactioncategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('transaction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['transactions.Transaction'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['transactions.Category'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=2)),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['foundations.Currency'])),
        ))
        db.send_create_signal('transactions', ['TransactionCategory'])

        # Adding model 'Envelope'
        db.create_table('transactions_envelope', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['transactions.Category'])),
        ))
        db.send_create_signal('transactions', ['Envelope'])

        # Adding model 'SalaryToEnvelope'
        db.create_table('transactions_salarytoenvelope', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('transaction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['transactions.Transaction'])),
            ('envelope', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['transactions.Envelope'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=2)),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['foundations.Currency'])),
        ))
        db.send_create_signal('transactions', ['SalaryToEnvelope'])

        # Adding model 'EnvelopeTransfer'
        db.create_table('transactions_envelopetransfer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_envelope', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['transactions.Envelope'])),
            ('to_envelope', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['transactions.Envelope'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=2)),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['foundations.Currency'])),
        ))
        db.send_create_signal('transactions', ['EnvelopeTransfer'])


    def backwards(self, orm):
        
        # Deleting model 'Account'
        db.delete_table('transactions_account')

        # Removing M2M table for field owner on 'Account'
        db.delete_table('transactions_account_owner')

        # Deleting model 'Transaction'
        db.delete_table('transactions_transaction')

        # Deleting model 'TransactionAssignment'
        db.delete_table('transactions_transactionassignment')

        # Deleting model 'Category'
        db.delete_table('transactions_category')

        # Deleting model 'TransactionCategory'
        db.delete_table('transactions_transactioncategory')

        # Deleting model 'Envelope'
        db.delete_table('transactions_envelope')

        # Deleting model 'SalaryToEnvelope'
        db.delete_table('transactions_salarytoenvelope')

        # Deleting model 'EnvelopeTransfer'
        db.delete_table('transactions_envelopetransfer')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'foundations.currency': {
            'Meta': {'object_name': 'Currency'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'rate': ('django.db.models.fields.DecimalField', [], {'default': '1.0', 'max_digits': '20', 'decimal_places': '10'}),
            'symbol': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'transactions.account': {
            'Meta': {'object_name': 'Account'},
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['foundations.Currency']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'owner': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'start_balance': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'})
        },
        'transactions.category': {
            'Meta': {'ordering': "('parent__name', 'name')", 'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['auth.User']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['transactions.Category']", 'null': 'True', 'blank': 'True'})
        },
        'transactions.envelope': {
            'Meta': {'object_name': 'Envelope'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['transactions.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'transactions.envelopetransfer': {
            'Meta': {'object_name': 'EnvelopeTransfer'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['foundations.Currency']"}),
            'from_envelope': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['transactions.Envelope']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to_envelope': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['transactions.Envelope']"})
        },
        'transactions.salarytoenvelope': {
            'Meta': {'object_name': 'SalaryToEnvelope'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['foundations.Currency']"}),
            'envelope': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['transactions.Envelope']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'transaction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['transactions.Transaction']"})
        },
        'transactions.transaction': {
            'Meta': {'object_name': 'Transaction'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original_description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'})
        },
        'transactions.transactionassignment': {
            'Meta': {'object_name': 'TransactionAssignment'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['transactions.Account']", 'null': 'True', 'blank': 'True'}),
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['foundations.Currency']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_reconciled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'transaction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['transactions.Transaction']"})
        },
        'transactions.transactioncategory': {
            'Meta': {'object_name': 'TransactionCategory'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['transactions.Category']"}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['foundations.Currency']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'transaction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['transactions.Transaction']"})
        }
    }

    complete_apps = ['transactions']
