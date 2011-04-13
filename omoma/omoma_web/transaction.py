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
"""
Custom transaction form
"""

import datetime
from decimal import Decimal

from django import forms
from django.forms.util import ErrorList
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from omoma.omoma_web.models import Account, Category, IOU, Transaction, \
                                   TransactionCategory, AutomaticCategory


class TransactionForm(forms.Form):
    """
    Custom form for transactions
    """

    TRANSACTION_TYPES = (
        ('Expense', 'Expense'),
        ('Income', 'Income'),
        ('Salary', 'Salary'),
        ('Transfer', 'Transfer'),
        ('Give', 'I gave money to...'),
        ('Receive', 'I received money from...'),
    )

    account = forms.CharField(label=_('Account'))
    date = forms.DateField(initial=datetime.date.today(), label=_('Date'))
    description = forms.CharField(label=_('Description'))
    amount = forms.DecimalField(label=_('Amount'), min_value=Decimal('0'))
    transaction_type = forms.ChoiceField(TRANSACTION_TYPES,
                                         widget=forms.RadioSelect,
                                         label=_('Transaction type'))
    category1 = forms.CharField(label=_('Category'), required=False)
    category1amount = forms.DecimalField(label=_('Amount'), required=False)
    category2 = forms.CharField(label=_('Category'), required=False)
    category2amount = forms.DecimalField(label=_('Amount'), required=False)
    category3 = forms.CharField(label=_('Category'), required=False)
    category3amount = forms.DecimalField(label=_('Amount'), required=False)
    destination_account = forms.CharField(label=_('Destination account'),
                                          required=False)
    peer1 = forms.CharField(label=_('Person'), required=False)
    peer1amount = forms.DecimalField(label=_('Amount'), required=False)
    peer2 = forms.CharField(label=_('Person'), required=False)
    peer2amount = forms.DecimalField(label=_('Amount'), required=False)
    peer3 = forms.CharField(label=_('Person'), required=False)
    peer3amount = forms.DecimalField(label=_('Amount'), required=False)

    def __init__(self, request, data=None, files=None, auto_id='id_%s',
                 prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=':', empty_permitted=False, instance=None):

        super(TransactionForm, self).__init__(data, files, auto_id, prefix,
                                              initial, error_class,
                                              label_suffix, empty_permitted)

        self.request = request
        self.__init_accounts()
        self.__init_categories()
        self.__init_peers()

        if instance:
            self.instance = instance
            self.__init_from_instance()
        else:
            self.instance = Transaction()

    def __init_categories(self):
        """
        Initialize categories lists
        """
        self.fields['category1'] = forms.ModelChoiceField( \
                                                       Category.objects.filter(
                                                      owner=self.request.user),
                                                           label=_('Category'),
                                                           required=False)
        self.fields['category2'] = forms.ModelChoiceField( \
                                                       Category.objects.filter(
                                                      owner=self.request.user),
                                                           label=_('Category'),
                                                           required=False)
        self.fields['category3'] = forms.ModelChoiceField( \
                                                       Category.objects.filter(
                                                      owner=self.request.user),
                                                           label=_('Category'),
                                                           required=False)

    def __init_peers(self):
        """
        Initialize peers lists (for IOUs)
        """
        self.fields['peer1'] = forms.ModelChoiceField(User.objects.all(),
                                                      label=_('Person'),
                                                      required=False)
        self.fields['peer2'] = forms.ModelChoiceField(User.objects.all(),
                                                      label=_('Person'),
                                                      required=False)
        self.fields['peer3'] = forms.ModelChoiceField(User.objects.all(),
                                                      label=_('Person'),
                                                      required=False)

    def __init_accounts(self):
        """
        Initialize accounts lists with accounts owned by the user
        """
        self.fields['account'] = forms.ModelChoiceField(Account.objects.filter(
                                                      owner=self.request.user),
                                                        empty_label=None,
                                                        label=_('Account'))
        self.fields['destination_account'] = \
                                 forms.ModelChoiceField(Account.objects.filter(
                                                      owner=self.request.user),
                                                label=_('Destination account'),
                                                        required=False)

    def __init_from_instance(self):
        """
        Initialize form data from instance data
        """
        self.fields['account'].initial = self.instance.account
        self.fields['date'].initial = self.instance.date
        self.fields['description'].initial = self.instance.description
        self.fields['amount'].initial = abs(self.instance.amount)

        my_ious = IOU.objects.filter(transaction=self.instance)

        if my_ious:
            if my_ious[0].money_transaction:
                if self.instance.amount < 0 and request.user in \
                      my_ious[0].recipient_transaction.account.owner.all():
                    self.fields['transaction_type'].initial = 'Trans'
                    self.fields['destination_account'].initial = \
                                   my_ious[0].recipient_transaction.account
                elif self.instance.amount < 0:
                    self.fields['transaction_type'].initial = 'Give'
                elif self.instance.amount > 0:
                    self.fields['transaction_type'].initial = 'Receive'
            elif self.instance.amount < 0:
                self.fields['transaction_type'].initial = 'Expense'

        elif self.instance.amount < 0:
            self.fields['transaction_type'].initial = 'Expense'

        elif self.instance.amount > 0:
            if self.instance.salary:
                self.fields['transaction_type'].initial = 'Salary'
            else:
                self.fields['transaction_type'].initial = 'Income'

        for num, category in enumerate(TransactionCategory.objects.filter( \
                                                   transaction=self.instance)):
            self.fields['category%d' % (num+1)].initial = category.category
            self.fields['category%damount' % (num+1)].initial = category.amount

        if self.fields['transaction_type'] != 'Trans':
            for num, iou in enumerate(my_ious):
                self.fields['peer%d' % (num+1)].initial = iou.recipient
                self.fields['peer%damount' % (num+1)].initial = iou.amount


    def clean(self):
        """
        Clean the form.
        """
        cleaned_data = self.cleaned_data

        transaction_type = cleaned_data.get('transaction_type')
        destination_account = cleaned_data.get('destination_account')
        peer1 = cleaned_data.get('peer1')

        if transaction_type == 'Transfer' and not destination_account:
            msg = _('A transfer needs a destination account.')
            self._errors['destination_account'] = self.error_class([msg])
        elif transaction_type == 'Give' and not peer1:
            msg = _('Who did you give this money to?')
            self._errors['peer1'] = self.error_class([msg])
        elif transaction_type == 'Receive' and not peer1:
            msg = _('Who gave you this money?')
            self._errors['peer1'] = self.error_class([msg])

        return cleaned_data


    def save(self):
        """
        Save the instance
        """

        # Values that are the same whatever the transaction type is
        self.instance.account = self.cleaned_data['account']
        self.instance.date = self.cleaned_data['date']
        self.instance.description = self.cleaned_data['description']
        self.instance.validated = False
        self.instance.deleted = False

        amount = self.cleaned_data['amount']
        transaction_type = self.cleaned_data['transaction_type']

        if transaction_type == 'Expense':
            self.instance.amount = -amount
            self.instance.salary = False
            self.is_money_transaction = False

        elif transaction_type == 'Income':
            self.instance.amount = amount
            self.instance.salary = False
            self.is_money_transaction = False

        elif transaction_type == 'Salary':
            self.instance.amount = amount
            self.instance.salary = True
            self.is_money_transaction = False

        elif transaction_type == 'Transfer':
            self.instance.amount = -amount
            self.instance.salary = False
            self.is_money_transaction = True

        elif transaction_type == 'Give':
            self.instance.amount = -amount
            self.instance.salary = False
            self.is_money_transaction = True

        elif transaction_type == 'Receive':
            self.instance.amount = amount
            self.instance.salary = False
            self.is_money_transaction = True

        self.instance.save()

        self.__set_categories(self.__list_categories())
        if transaction_type == 'Transfer':
            self.__set_transfer()
        else:
            self.__set_peers(self.__list_peers())


        description_to_match = self.instance.description.lower()

        categories = AutomaticCategory.objects.filter( \
                                             category__owner=self.request.user)
        for category in categories:
            if category.description in description_to_match:
                TransactionCategory(transaction=self.instance,
                                    category=category.category).save()

    def __list_categories(self):
        """
        Return selected categories in a dict

        {category: amount}
        """
        category1 = self.cleaned_data['category1']
        category1amount = self.cleaned_data['category1amount']
        category2 = self.cleaned_data['category2']
        category2amount = self.cleaned_data['category2amount']
        category3 = self.cleaned_data['category3']
        category3amount = self.cleaned_data['category3amount']
        categories = {}
        if category1:
            if category1amount:
                categories[category1] = category1amount
            else:
                categories[category1] = True
        if category2:
            if category2amount:
                categories[category2] = category2amount
            else:
                categories[category2] = True
        if category3:
            if category3amount:
                categories[category3] = category3amount
            else:
                categories[category3] = True

        return categories

    def __list_peers(self):
        """
        Return selected peers as a dict

        {peer: amount}
        """
        amount = self.cleaned_data['amount']
        peer1 = self.cleaned_data['peer1']
        peer1amount = self.cleaned_data['peer1amount']
        peer2 = self.cleaned_data['peer2']
        peer2amount = self.cleaned_data['peer2amount']
        peer3 = self.cleaned_data['peer3']
        peer3amount = self.cleaned_data['peer3amount']
        peers = {}
        peers_total = 0
        noamount_peers = []
        if peer1:
            if peer1amount:
                peers[peer1] = peer1amount
                peers_total = peers_total + peer1amount
            else:
                noamount_peers.append(peer1)
        if peer2:
            if peer2amount:
                peers[peer2] = peer2amount
                peers_total = peers_total + peer2amount
            else:
                noamount_peers.append(peer2)
        if peer3:
            if peer3amount:
                peers[peer3] = peer3amount
                peers_total = peers_total + peer3amount
            else:
                noamount_peers.append(peer3)
        if len(noamount_peers):
            remainingamount = amount - peers_total
            dividedamount = remainingamount / (len(noamount_peers) + 1)
            for peer in noamount_peers:
                peers[peer] = dividedamount

        return peers

    def __set_categories(self, categories):
        """
        Set transaction categories according to selected categories
        """
        instancecategories = TransactionCategory.objects.filter( \
                                                     transaction=self.instance)

        for category in instancecategories:
            amount = categories.pop(category.category, None)
            if amount == True:
                if category.amount != None:
                    category.amount = None
                    category.save()
            elif amount:
                if category.amount != amount:
                    category.amount = amount
                    category.save()
            else:
                category.delete()

        # The only categories remaining in the dict are the one that were not
        # already linked to the transaction
        for category in categories.items():
            if category[1] == True:
                TransactionCategory(transaction=self.instance,
                                    category=category[0]).save()
            else:
                TransactionCategory(transaction=self.instance,
                                    category=category[0],
                                    amount=category[1]).save()

    def __set_peers(self, peers):
        """
        Set transaction IOUs according to selected peers
        """
        instanceious = IOU.objects.filter(transaction=self.instance)

        for iou in instanceious:
            amount = peers.pop(iou.recipient, None)
            if amount:
                if iou.amount != amount:
                    iou.amount = amount
                    iou.accepted = 'p'
                    iou.save()
            else:
                iou.delete()

        # The only IOUs remaining in the dict are the one that were not
        # already linked to the transaction
        for peer in peers.items():
            IOU(owner=self.request.user, transaction=self.instance,
                recipient=peer[0], amount=peer[1],
                money_transaction=self.is_money_transaction).save()

    def __set_transfer(self):
        """
        Set destination transaction and according IOU when this is a transfer
        """
        instanceious = IOU.objects.filter(transaction=self.instance)

        myself = self.request.user
        dest_account = self.cleaned_data['destination_account']
        amount = self.cleaned_data['amount']

        exists = False
        for iou in instanceious:
            if iou.recipient == myself:
                if iou.amount == amount and \
                   iou.recipient_transaction.amount == amount and \
                   iou.recipient_transaction.account == dest_account and \
                   not exists:
                    exists = True
                else:
                    iou.recipient_transaction.delete()
                    iou.delete()
            else:
                iou.delete()

        if not exists:
            dest_transaction = Transaction(account=dest_account,
                                           date=self.instance.date,
                                         description=self.instance.description,
                                           amount=amount,
                                           original_description=description)
            dest_transaction.save()
            IOU(owner=myself, transaction=self.instance,
                recipient=myself, amount=amount, money_transaction=True,
                recipient_transaction=dest_transaction, accepted='a').save()
