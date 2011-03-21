# Django models for Omoma
# Copyright 2011 Sebastien Maccagnoni-Munch
#
# This file is part of Omoma.
#
# Omoma is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# Omoma is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Omoma. If not, see <http://www.gnu.org/licenses/>.

from django import forms
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q, Sum
from django.utils.translation import ugettext as _


class Currency(models.Model):
    """
    A currency, to be linked with accounts

    Change rate is relative to any currency whose rate is 1.
    For example, if "euro" is 1 and "dollar" is 1.2,
    then 1 dollar = 0.83 euro

    The short name could be the sign representing the currency ($, etc...)
    """
    name = models.CharField(max_length=100, verbose_name=_('name'))
    short_name = models.CharField(max_length=10, verbose_name=_('short name'))
    rate = models.DecimalField(max_digits=10, decimal_places=2,
                               default=1.00, verbose_name=_('change rate'))

    def __unicode__(self):
        return self.fullname()

    def fullname(self):
        """
        Full name of the currency (name and short_name)
        """
        return "%s (%s)" % (self.name, self.short_name)

    class Meta:
        verbose_name = _('currency')
        verbose_name_plural = _('currencies')


class Account(models.Model):
    """
    An account, owned by one or multiple users
    """
    owner = models.ManyToManyField(User, verbose_name=_('owner'))
    name = models.CharField(max_length=200, verbose_name=_('name'))
    currency = models.ForeignKey('Currency', verbose_name=_('currency'))
    start_balance = models.DecimalField(max_digits=14, decimal_places=2,
                                        verbose_name=_('start balance'))

    def __unicode__(self):
        return self.name

    def current_balance(self):
        """
        Last balance of the account
        """
        ts = Transaction.objects.filter(account=self,
                                        deleted=False).aggregate(Sum('amount'))
        if ts['amount__sum']:
            return self.start_balance + ts['amount__sum']
        else:
            return self.start_balance

    def validated_balance(self):
        """
        Last validated balance of this account
        """
        ts = Transaction.objects.filter(account=self, deleted=False,
                                       validated=True).aggregate(Sum('amount'))
        if ts['amount__sum']:
            return self.start_balance + ts['amount__sum']
        else:
            return self.start_balance

    def count_transactions(self):
        """
        Number of transactions in this account
        """
        return len(Transaction.objects.filter(account=self))

    class Meta:
        verbose_name = _('account')
        verbose_name_plural = _('accounts')


class Transaction(models.Model):
    """
    A transaction, which is always linked to an account

    A positive amount represents an income,
    a negative amount represents an expenditure.

    Original description is, for example, the description in the bank account.

    If ``salary`` is true, the transaction is a salary, and it is dispatched
    accordingly to the existing envelopes.

    The validation may be useful for automatic transaction creation,
    where you want to validate the transaction when acknowledgeing it
    """
    account = models.ForeignKey('Account', verbose_name=_('account'))
    date = models.DateField(verbose_name=_('date'))
    description = models.CharField(max_length=500,
                                   verbose_name=_('description'))
    amount = models.DecimalField(max_digits=14, decimal_places=2,
                                 verbose_name=_('amount'))
    original_description = models.CharField(max_length=500, null=True,
                            blank=True, verbose_name=_('original description'))
    salary = models.BooleanField(default=False, verbose_name=_('salary'))
    validated = models.BooleanField(default=False, verbose_name=_('validated'))
    deleted = models.BooleanField(default=False, verbose_name=_('deleted'))

    def shared_remaining_amount(self):
        """
        Amount for each TransactionCategory which
        amount has not been specified
        """
        transactioncategorys = TransactionCategory.objects.filter(
                                                              transaction=self)
        countcategories = 0
        availableamount = abs(self.amount)
        for transactioncategory in transactioncategorys:
            if transactioncategory.amount:
                availableamount = availableamount - transactioncategory.amount
            else:
                countcategories = countcategories + 1
        return availableamount/countcategories

    def has_iou(self):
        """
        True if there is any IOU referring to this transaction
        """
        ious = IOU.objects.filter(Q(transaction=self) |
                                 Q(recipient_transaction=self))
        if ious:
            return True
        else:
            return False

    def __unicode__(self):
        return self.description

    class Meta:
        ordering = ['-date']
        verbose_name = _('transaction')
        verbose_name_plural = _('transactions')


class Category(models.Model):
    """
    A transaction category

    Budgets are based on the categories
    """
    owner = models.ForeignKey(User, related_name='+', verbose_name=_('owner'))
    parent = models.ForeignKey('Category', null=True, blank=True,
                               verbose_name=_('parent'))
    name = models.CharField(max_length=200, verbose_name=_('name'))

    def __unicode__(self):
        if self.parent:
            name = '>'.join((unicode(self.parent), self.name))
        else:
            name = self.name
        return name

    def count_transactions(self):
        """
        Number of transactions on this account
        """
        return len(TransactionCategory.objects.filter(category=self))

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')


class TransactionCategory(models.Model):
    """
    A transaction can have multiple categories

    Within a single transaction, categories amounts are added one to another,
    limited by the transaction's amount.

    A null category amount means "the rest". If there are multiple
    null amounts, then "the rest" is divided amongst them.
    """
    transaction = models.ForeignKey('Transaction',
                                    verbose_name=_('transaction'))
    category = models.ForeignKey('Category', verbose_name=_('category'))
    amount = models.DecimalField(max_digits=14, decimal_places=2, null=True,
                                 blank=True, verbose_name=_('amount'))

    def resulting_amount(self):
        """
        Amount of this TransactionCategory (manually defined
        or calculated according to the Transaction)
        """
        if self.amount:
            return self.amount
        else:
            return self.transaction.shared_remaining_amount()

    def clean(self):
        """
        Clean the amount, because amounts shall be positive

        (income or outcome are based on the transaction's amount)
        """
        if self.amount: self.amount = abs(self.amount)

    def __unicode__(self):
        return _('%(category)s for "%(transaction)s"') % {
                                                 'category':self.category.name,
                                    'transaction':self.transaction.description}

    class Meta:
        verbose_name = _('transaction category')
        verbose_name_plural = _('transaction categories')
        unique_together = ('transaction', 'category')


class IOU(models.Model):
    """
    An IOU is when you owe something to someone or
    when someones owes something to you

    A positive amount means "you owe X to the recipient",
    a negative amount means "the recipient owes you X".

    The amount of the IOU (can be less than the transaction, for example when
    you pay at the restaurant and want to get reimbursed only for the half)

    If ``money_transaction`` is True, this IOU represents a money transfer to
    or from the recipient (for example you lent money), and therefore needs
    a recipient transaction when it is accepted

    If False it represents something you paid for him or received in his name

    ``accepted`` can be:

    * ``a``: accepted
    * ``r``: rejected
    * ``p``: pending
    """
    ACCEPTED_CHOICES = (
        ('a', _('accepted')),
        ('r', _('rejected')),
        ('p', _('pending'))
    )

    owner = models.ForeignKey(User, verbose_name=_('owner'))
    transaction = models.ForeignKey('Transaction',
                                    verbose_name=_('transaction'))
    recipient = models.ForeignKey(User, related_name='+',
                                  verbose_name=_('recipient'))
    amount = models.DecimalField(max_digits=14, decimal_places=2,
                                 verbose_name=_('amount'))
    money_transaction = models.BooleanField(default=False,
                                           verbose_name=_('money transaction'))
    recipient_transaction = models.ForeignKey('Transaction', null=True,
                           blank=True, related_name='recipient_transaction_id',
                                       verbose_name=_('recipient transaction'))
    accepted = models.CharField(max_length=1, choices=ACCEPTED_CHOICES,
                                default='p', verbose_name=_('accepted'))

    def __unicode__(self):
        return _('IOU for "%(transaction)s" to "%(recipient)s"') % {
                                    'transaction':self.transaction.description,
                                           'recipient':self.recipient.username}

    def clean(self):
        """
        Clean the amount, because amounts shall be positive

        (income or outcome are based on the transaction's amount)
        """
        if self.amount: self.amount = abs(self.amount)

    def recipienttype(self):
        """
        String representing the type of this IOU for its recipient
        """
        if self.money_transaction:
            if self.transaction.amount > 0:
                return _('He/she received from me')
            else:
                return _('He/she gave to me')
        else:
            if self.transaction.amount > 0:
                return _('He/she received for me')
            else:
                return _('He/she paid for me')

    def ownertype(self):
        """
        String representing the type of this IOU for its owner
        """
        if self.money_transaction:
            if self.transaction.amount > 0:
                return _('I received from him/her')
            else:
                return _('I gave to him/her')
        else:
            if self.transaction.amount > 0:
                return _('I received for him/her')
            else:
                return _('I paid for him/her')
    class Meta:
        ordering = ['-transaction__date']
        verbose_name = _('IOU')
        verbose_name_plural = _('IOUs')
        unique_together = ('transaction', 'recipient')


class Budget(models.Model):
    """
    A budget is an amount you do not want to exceed in a given period

    ``period_length`` may be :

    * ``y``: year (12 months)
    * ``s``: semester (6 months)
    * ``q``: quarter (3 months)
    * ``m``: month (28 to 31 days)
    * ``w``: week (7 days)
    * ``v``: envelope, this is a special case...

    Each time you receive a salary, it is dispateched in all envelopes.
    Envelopes do not expire like budgets : they are feed by salaries

    If your salary is less than the total envelopes credits amount, all
    envelopes are credited equally less.

    If an envelope is defined as a number smaller than 1, it is interpreted as
    "a percentage of what remains after substracting the fix amount envelopes".
    It may be useful if your salary is irregular.
    """
    PERIOD_LENGTH_CHOICES = (
        ('y', _('year (12 months)')),
        ('s', _('semester (6 months)')),
        ('q', _('quarter (3 months)')),
        ('m', _('month (28 to 31 days)')),
        ('w', _('week (7 days)')),
        ('v', _('envelope'))
    )
    category = models.ForeignKey('Category', verbose_name=_('category'))
    period_start = models.DateField(null=True, blank=True,
                                                verbose_name=_('period start'))
    period_length = models.CharField(max_length=1,
                                     choices=PERIOD_LENGTH_CHOICES,
                                     default='m',
                                     verbose_name=_('period length'))
    limit = models.DecimalField(max_digits=14, decimal_places=2,
                                verbose_name=_('limit'))

    def __unicode__(self):
        return _('Budget for %s') % category

    class Meta:
        verbose_name = _('budget')
        verbose_name_plural = _('budgets')


class AccountForm(forms.ModelForm):

    class Meta:
        model = Account
        exclude = ('owner',)


class TransactionForm(forms.ModelForm):

    def __init__(self, request, *args, **kwargs):
        super (TransactionForm,self).__init__(*args, **kwargs)
        # Only return transactions owned by the person who requests
        self.fields['account'] = forms.ModelChoiceField(Account.objects.filter(
                                                        owner=request.user.id),
                                                        empty_label=None)

    class Meta:
        model = Transaction
        exclude = ('validated', 'deleted',)


class CategoryForm(forms.ModelForm):

    def __init__(self, request, *args, **kwargs):
        super (CategoryForm,self).__init__(*args, **kwargs)
        # Parent categories should be owned by the person who requests
        self.fields['parent'] = forms.ModelChoiceField(
                                   Category.objects.filter(owner=request.user),
                                                       required=False)

    class Meta:
        model = Category
        exclude = ('owner',)

class TransactionCategoryForm(forms.ModelForm):

    def __init__(self, request, *args, **kwargs):
        super (TransactionCategoryForm,self).__init__(*args, **kwargs)
        # Only return categories owned by the person who requests
        self.fields['category'] = forms.ModelChoiceField(
                                Category.objects.filter(owner=request.user.id),
                                                         empty_label=None)

    class Meta:
        model = TransactionCategory
        exclude = ('transaction',)


class IOUForm(forms.ModelForm):

    def __init__(self, request, *args, **kwargs):
        super (IOUForm,self).__init__(*args, **kwargs)

    class Meta:
        model = IOU
        exclude = ('owner', 'transaction',
                   'recipient_transaction', 'accepted',)