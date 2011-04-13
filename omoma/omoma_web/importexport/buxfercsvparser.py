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
Buxfer CSV import parser for Omoma
"""

import cStringIO
import csv
import datetime
import decimal

from django import forms
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from omoma.omoma_web.models import Account, Category, IOU
from omoma.omoma_web.models import Transaction, TransactionCategory


def name():
    """
    Return the parser's name
    """
    return 'Buxfer CSV export (migration from Buxfer)'


def check(filedata):
    """
    Check if the data fits to this parser
    """
    return filedata[:24] == '"Transactions matching ['


# pylint: disable=E1101,W0232,R0903
class DetailsForm(forms.Form):
    """
    Buxfer CSV details form
    """
    createcategories = forms.BooleanField(required=False,
                                 label=_('Create categories when unspecified'))

    # pylint: disable=E1002
    def __init__(self, request, *args, **kwargs):
        aid = kwargs.pop('aid', None)
        super(DetailsForm, self).__init__(*args, **kwargs)
        self.request = request

        for person in request.session['importparser']['parser'].all_people:
            self.fields['person%s' % slugify(person)] = forms.ModelChoiceField(
                                                            User.objects.all(),
                                               label=_(person.decode('utf-8')))

        for account in request.session['importparser']['parser'].all_accounts:
            if account == '(none)':
                accountlabel = _('Transactions without account')
            else:
                accountlabel = _('Account "%s"') % account.decode('utf-8')

            aas = Account.objects.filter(owner=request.user,
                                         name__iexact=account)
            if aas:
                initialaccount = aas[0]
            else:
                initialaccount = aid
            self.fields['account%s' % slugify(account)] = \
                                                        forms.ModelChoiceField(
                                    Account.objects.filter(owner=request.user),
                                    initial=initialaccount, label=accountlabel)

        for tag in request.session['importparser']['parser'].all_tags:
            ccs = Category.objects.filter(owner=request.user, name__iexact=tag)
            if ccs:
                initialcategory = ccs[0]
            else:
                initialcategory = None
            self.fields['tag%s' % slugify(tag)] = forms.ModelChoiceField(
                                   Category.objects.filter(owner=request.user),
                                       initial=initialcategory, required=False,
                                     label=_('Tag "%s"' % tag.decode('utf-8')))


class Parser:
    """
    The parser
    """

    transactions = []
    index = {}

    def __init__(self, filedata):
        filestream = cStringIO.StringIO(filedata)
        filestream.next()
        headers = filestream.next().split(',')

        self.index['date'] = headers.index('Date')
        self.index['description'] = headers.index('Description')
        self.index['amount'] = headers.index('Amount')
        self.index['type'] = headers.index('Type')
        tagindex = headers.index('Tags')
        self.index['tags'] = tagindex
        accindex = headers.index('Account')
        self.index['account'] = accindex
        self.index['status'] = headers.index('Status')
        self.index['me'] = 8
        for num, person in enumerate(headers[9:]):
            self.index[person] = num+9

        currencies = {}
        accounts = {}
        tags = {}

        for transactionline in csv.reader(filestream):
            self.transactions.append(transactionline)

            # List all accounts
            this_accounts = transactionline[accindex]
            for acccount in this_accounts.split('->'):
                accounts[acccount.strip()] = True
            # List all categories
            this_tags = transactionline[tagindex]
            for tag in this_tags.split(','):
                if tag.strip():
                    tags[tag.split(':')[0].strip()] = True

        self.all_currencies = currencies.keys()
        self.all_accounts = accounts.keys()
        self.all_tags = tags.keys()
        self.all_people = headers[9:]

    def parse(self, form):
        """
        Parse a Buxfer CSV file.

        /!\ With Buxfer CSV files, if a transaction already exists
        it is duplicated.
        """

        createcategories = form.cleaned_data.get('createcategories')

        currencies = {}
        people = {}
        accounts = {}
        tags = {}
        for field in form.fields.keys():
            if field.startswith('currency'):
                currencies[field[8:]] = form.cleaned_data.get(field)
            elif field.startswith('person'):
                people[field[6:]] = form.cleaned_data.get(field)
            elif field.startswith('account'):
                acct = form.cleaned_data.get(field)
                if acct:
                    if not form.request.user in acct.owner.all():
                        return False
                    accounts[field[7:]] = acct
            elif field.startswith('tag'):
                cat = form.cleaned_data.get(field)
                if cat:
                    if cat.owner != form.request.user:
                        return False
                    tags[field[3:]] = form.cleaned_data.get(field)

        for line in self.transactions:

            # Make IOUs for the Transaction
            # Examples :
            #  ('iou', recipient object, value, is a money transfer (boolean))
            #  ('transfer', destination account object)
            make_ious = []
            # Link the following tags to this Transaction
            #  (tag name, amount)
            make_categories = []

            transaction = Transaction()

            accountname = line[self.index['account']].split('->')[0].strip()
            destaccount = accounts.get(slugify(accountname), None)
            if destaccount:
                transaction.account = destaccount
            else:
                # If no account, no transaction !
                continue

            origtype = line[self.index['type']]
            amount = line[self.index['amount']].lstrip('+ ').replace('.', '').\
                                                             replace(',', '.')
            origamount = decimal.Decimal(amount)
            tagsline = line[self.index['tags']]
            if tagsline.strip():
                origtags = line[self.index['tags']].split(',')
                for cat in origtags:
                    splitcat = cat.split(':')
                    if len(splitcat) > 1:
                        value = decimal.Decimal(splitcat[1])
                    else:
                        value = origamount / len(origtags)
                    make_categories.append((splitcat[0], value))

            myaction = line[self.index['me']][:3]

            if origtype == 'Expense':
                # I'm spending money for myself
                transaction.amount = -origamount

            elif origtype in ('Income', 'Refund'):
                # I'm receiving money
                transaction.amount = origamount

            elif origtype in ('Paid for friend', 'Split bill') and \
                 myaction == 'Get':
                # I'm paying something for someone else
                transaction.amount = -origamount
                for personid, person in enumerate(line[9:]):
                    if person.startswith('Owe'):
                        value = person[4:].replace('.', '').replace(',', '.')
                        value = decimal.Decimal(value)
                        personobj = people[slugify(self.all_people[personid])]
                        make_ious.append(('iou', personobj, value, False))

            elif origtype in ('Paid for friend', 'Split bill') and \
                 myaction == 'Owe':
                # Someone paid something for me
                continue
                # That's not an IOU on my side...

            elif origtype in ('Settlement', 'Loan') and myaction == 'Get':
                # I give money to someone
                transaction.amount = -origamount
                for personid, person in enumerate(line[9:]):
                    if person.startswith('Get'):
                        value = person[4:].replace('.', '').replace(',', '.')
                        value = decimal.Decimal(value)
                        personobj = people[slugify(self.all_people[personid])]
                        make_ious.append(('iou', personobj, value, True))

            elif origtype in ('Settlement', 'Loan') and myaction == 'Owe':
                # I receive money from someone
                transaction.amount = origamount
                for personid, person in enumerate(line[9:]):
                    if person.startswith('Get'):
                        value = person[4:].replace('.', '').replace(',', '.')
                        value = decimal.Decimal(value)
                        personobj = people[slugify(self.all_people[personid])]
                        make_ious.append(('iou', personobj, value, True))

            elif origtype == 'Transfer':
                # Transfer between two of my accounts
                transaction.amount = -origamount
                try:
                    destinationaccount = line[self.index['account']].\
                                                         split('->')[1].strip()
                    recipientaccount = accounts[slugify(destinationaccount)]
                except KeyError:
                    # The recipient account does not exist
                    continue
                make_ious.append(('transfer', recipientaccount))

            transaction.date = datetime.datetime.strptime(\
                                          line[self.index['date']], '%Y-%m-%d')
            transaction.original_description = line[self.index['description']]
            if line[self.index['status']] == 'Reconciled':
                transaction.validated = True

            import_transaction(form.request, transaction, duplicate=True)

            if transaction:
                for thistag in make_categories:
                    cat = tags.get(thistag[0], None)
                    if not cat:
                        if createcategories:
                            cat = Category(owner=form.request.user,
                                           name=thistag[0])
                            cat.save()
                            tags[thistag[0]] = cat
                            tcat = TransactionCategory(transaction=transaction,
                                                       category=cat,
                                                       amount=thistag[1])
                            tcat.save()
                    else:
                        tcat = TransactionCategory(transaction=transaction,
                                                   category=cat,
                                                   amount=thistag[1])
                        tcat.save()

                for iou in make_ious:
                    if iou[0] == 'iou':
                        iou = IOU(owner=form.request.user,
                                  transaction=transaction,
                                  recipient=iou[1], amount=iou[2],
                                  money_transaction=iou[3])
                        iou.save()
                    elif iou[0] == 'transfer':
                        recipienttrans = Transaction(account=iou[1],
                                                     date=transaction.date,
                                           description=transaction.description,
                                                    amount=-transaction.amount,
                                               validated=transaction.validated)
                        recipienttrans.save()

                        iou = IOU(owner=form.request.user,
                                  transaction=transaction,
                                  recipient=form.request.user,
                                  amount=abs(transaction.amount),
                                  money_transaction=True,
                                  recipient_transaction=recipienttrans,
                                  accepted='a')
                        iou.save()

        return ''
