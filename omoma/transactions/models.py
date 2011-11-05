from django import forms
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _

from gadjo.requestprovider.signals import get_request

from omoma.foundations.models import Currency



class Account(models.Model):
    """
    An account

    - owner: the owner of the account
    - name: the name of the account
    - currency: the default currency of the account
    - start_balance: the starting balance of the account
    """
    owner = models.ManyToManyField(User, verbose_name=_('owner'))
    name = models.CharField(max_length=200, verbose_name=_('name'))
    currency = models.ForeignKey(Currency, verbose_name=_('currency'))
    start_balance = models.DecimalField(max_digits=14, decimal_places=2, verbose_name=_('start balance'))

    def __unicode__(self):
        return self.name

    @property
    def balance(self):
        # TODO Calculate the account's balance
        return self.start_balance

    @property
    def balance_as_string(self):
        return _('%(currency)s%(value).2f') % {'value':self.balance, 'currency':self.currency.symbol}

    def balance_in_currency(self, currency):
        return self.balance * self.currency.rate / currency.rate

    def balance_in_currency_as_string(self, currency):
        return _('%(currency)s%(value).2f') % {'value':self.balance_in_currency(currency), 'currency':currency.symbol}

    class Meta:
        verbose_name = _('account')
        verbose_name_plural = _('accounts')


class Transaction(models.Model):
    """
    A transaction

    - description: the transaction's description (one-line)
    - original_description: the transaction's original description (especially with automatic imports)
    """
    description = models.CharField(max_length=500, verbose_name=_('description'))
    original_description = models.CharField(max_length=500, null=True, blank=True, verbose_name=_('original description'))

    def __unicode__(self):
        """
        Full name of the transaction
        """
        return self.description



class TransactionAssignment(models.Model):
    """
    An assignment of a transaction to an account

    - transaction: the transaction
    - account: the account (may be null)
    - amount: the amount of money from or to this transaction
    - currency: the currency for this amount (if null, taken from the account)
    - is_reconciled: is this assignment reconciled (verified with the bank information)
    """
    transaction = models.ForeignKey('Transaction', verbose_name=_('transaction'))
    account = models.ForeignKey('Account', null=True, blank=True, verbose_name=_('account'))
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name=_('amount'))
    currency = models.ForeignKey(Currency, null=True, blank=True, verbose_name=_('currency'))
    is_reconciled = models.BooleanField(default=False, verbose_name=_('is reconciled'))

    def __unicode__(self):
        """
        Full name of the transaction assignment
        """
        return _('%(amount)s for %(transaction)s') % {'amount':self.amount, 'transaction':self.transaction}

    class Meta:
        verbose_name = _('transaction assignment')
        verbose_name_plural = _('transactions assignments')



class Category(models.Model):
    """
    A transaction category

    - owner: the category's owner
    - parent: the category's parent
    - name: the category's name
    - fullname: the category's name with its parent's name (automatically filled)
    """
    owner = models.ForeignKey(User, related_name='+', verbose_name=_('owner'))
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', verbose_name=_('parent'))
    name = models.CharField(max_length=200, verbose_name=_('name'))
    fullname = models.CharField(max_length=1000, blank=True, verbose_name=_('name'))

    def __unicode__(self):
        return self.fullname

    def save(self, *args, **kwargs):
        if self.parent:
            self.fullname = '%s > %s' % (self.parent.fullname, self.name)
        else:
            self.fullname = self.name
        super(Category, self).save(*args, **kwargs)
        for child in self.children.all():
            child.save()

    class Meta:
        ordering = ('fullname',)
        verbose_name = _('category')
        verbose_name_plural = _('categories')



class TransactionCategory(models.Model):
    """
    A link from a transaction to a category

    - transaction: the transaction
    - category: the category
    - amount: the amount of the assignment
    - currency: the currency of this amount
    """
    transaction = models.ForeignKey('Transaction', verbose_name=_('transaction'))
    category = models.ForeignKey('Category', verbose_name=_('category'))
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name=_('amount'))
    currency = models.ForeignKey(Currency, verbose_name=_('currency'))

    def __unicode__(self):
        return _('%(category)s for "%(transaction)s"') % { 'category': self.category.name, 'transaction': self.transaction.description }

    class Meta:
        verbose_name = _('transaction category')
        verbose_name_plural = _('transaction categories')



class Envelope(models.Model):
    """
    An envelope

    - category: the category this envelope is linked to
    """
    category = models.ForeignKey('Category', verbose_name=_('category'))

    def __unicode__(self):
        return self.category

    class Meta:
        verbose_name = _('envelope')
        verbose_name_plural = _('envelopes')



class SalaryToEnvelope(models.Model):
    """
    A link from a salary to an envelope

    When a money income is not directly linked to a category, this model permits forcing attribution of parts of it to an envelope without putting it into the corresponding category.

    - transaction: the corresponding transaction
    - envelope: the corresponding envelope
    - amount: the amount of money to put into this envelope
    - currency: the corresponding currency
    """
    transaction = models.ForeignKey('Transaction', verbose_name=_('transaction'))
    envelope = models.ForeignKey('Envelope', verbose_name=_('envelope'))
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name=_('amount'))
    currency = models.ForeignKey(Currency, verbose_name=_('currency'))


    def __unicode__(self):
        return _('%(amount)s from %(transaction)s into %(category)s') % {'amount': self.amount, 'transaction': self.transaction, 'category': self.envelope.category}

    class Meta:
        verbose_name = _('salary to envelope')
        verbose_name_plural = _('salary to envelopes')



class EnvelopeTransfer(models.Model):
    """
    A transfer from one envelope to another

    If there isn't enough money left in an envelope, money can be transferred from another envelope
    Money can also virtually be "created" into envelopes or "removed" from envelopes
    """
    from_envelope = models.ForeignKey('Envelope', related_name='+', verbose_name=_('from envelope'))
    to_envelope = models.ForeignKey('Envelope', related_name='+', verbose_name=_('to envelope'))
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name=_('amount'))
    currency = models.ForeignKey(Currency, verbose_name=_('currency'))

    class Meta:
        verbose_name = _('envelope transfer')
        verbose_name_plural = _('envelopes transfers')
