# Buxfer CSV import parser for Omoma
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

import cStringIO
import csv
import datetime
import decimal

from django import forms
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from omoma_web.importexport import import_transaction
from omoma_web.models import Account, Category, Currency, IOU, Transaction, \
                             TransactionCategory


def name():
    return 'Buxfer CSV export (migration from Buxfer)'


def check(filedata):
    return filedata[:24] == '"Transactions matching ['


class DetailsForm(forms.Form):
    """
    Buxfer CSV details form
    """
    createcategories = forms.BooleanField(required=False,
                                 label=_('Create categories when unspecified'))
    createimportaccount = forms.BooleanField(initial=True, required=False,
            label=_('Create a special account for unbound IOUs (recommended)'))

    def __init__(self, request, *args, **kwargs):
        aid = kwargs.pop('aid', None)
        super (DetailsForm,self).__init__(*args, **kwargs)
        self.request = request

        firstperson = True
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
            self.fields['account%s' % slugify(account)] = forms.ModelChoiceField(
                                    Account.objects.filter(owner=request.user),
                                        initial=initialaccount, required=False,
                                                            label=accountlabel)

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

        for t in csv.reader(filestream):
            self.transactions.append(t)

            # List all accounts
            this_accounts = t[accindex]
            for ac in this_accounts.split('->'):
                accounts[ac.strip()] = True
            # List all categories
            this_tags = t[tagindex]
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

        # Create the special account for unbound IOUs
        if form.cleaned_data.get('createimportaccount'):
            importdate = datetime.datetime.now().strftime('%Y-%m-%d')

            unboundaccount = Account.objects.create(start_balance=0,
                          name=_('Unbound IOUs, Buxfer import on %(date)s') % \
                                                           {'date':importdate},
                                           currency=Currency.objects.get(pk=1))
            unboundaccount.owner.add(form.request.user)
            unboundaccount.save()
        else:
            unboundaccount = False

        createcategories = form.cleaned_data.get('createcategories')

        currencies = {}
        people = {}
        accounts = {}
        tags = {}
        for f in form.fields.keys():
            if f.startswith('currency'):
                currencies[f[8:]] = form.cleaned_data.get(f)
            elif f.startswith('person'):
                people[f[6:]] = form.cleaned_data.get(f)
            elif f.startswith('account'):
                acct = form.cleaned_data.get(f)
                if acct:
                    if not form.request.user in acct.owner.all():
                        return False
                    accounts[f[7:]] = acct
            elif f.startswith('tag'):
                cat = form.cleaned_data.get(f)
                if cat:
                    if cat.owner != form.request.user:
                        return False
                    tags[f[3:]] = form.cleaned_data.get(f)

        for line in self.transactions:

            # Make IOUs for the Transaction
            # Examples :
            #  ('iou', recipient object, value, is a money transfer (boolean))
            #  ('transfer', destination account object)
            make_ious = []
            # Link the following tags to this Transaction
            #  (tag name, amount)
            make_categories = []

            t = Transaction()

            destaccount = accounts.get(slugify(line[self.index['account']].split('->')[0].strip()), None)
            if destaccount:
                t.account = destaccount
            elif unboundaccount:
                t.account = unboundaccount
            else:
                # If no account, no transaction !
                continue

            origtype = line[self.index['type']]
            origamount = decimal.Decimal(line[self.index['amount']].lstrip('+ ').replace('.', '').replace(',', '.'))
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
                t.amount = -origamount

            elif origtype in ('Income', 'Refund'):
                # I'm receiving money
                t.amount = origamount

            elif (origtype == 'Paid for friend' and myaction == 'Get') or \
                 (origtype == 'Split bill' and myaction == 'Get'):
                # I'm paying something for someone else
                t.amount = -origamount
                for personid, person in enumerate(line[9:]):
                    if person.startswith('Owe'):
                        value = decimal.Decimal(person[4:].replace('.', '').replace(',', '.'))
                        make_ious.append(('iou', people[slugify(self.all_people[personid])], value, False))

            elif (origtype == 'Paid for friend' and myaction == 'Owe') or \
                 (origtype == 'Split bill' and myaction == 'Owe'):
                # Someone paid something for me
                t.amount = origamount
                for personid, person in enumerate(line[9:]):
                    if person.startswith('Get'):
                        value = decimal.Decimal(person[4:].replace('.', '').replace(',', '.'))
                        make_ious.append(('iou', people[slugify(self.all_people[personid])], value, False))

            elif origtype == 'Settlement' and myaction == 'Get':
                # I give money to someone
                t.amount = -origamount
                for personid, person in enumerate(line[9:]):
                    if person.startswith('Get'):
                        value = decimal.Decimal(person[4:].replace('.', '').replace(',', '.'))
                        make_ious.append(('iou', people[slugify(self.all_people[personid])], value, True))

            elif origtype == 'Settlement' and myaction == 'Owe':
                # I receive money from someone
                t.amount = origamount
                for personid, person in enumerate(line[9:]):
                    if person.startswith('Get'):
                        value = decimal.Decimal(person[4:].replace('.', '').replace(',', '.'))
                        make_ious.append(('iou', people[slugify(self.all_people[personid])], value, True))

            elif origtype == 'Transfer':
                # Transfer between two of my accounts
                t.amount = -origamount
                try:
                    recipientaccount = accounts[slugify(line[self.index['account']].split('->')[1].strip())]
                except KeyError:
                    # The recipient account does not exist
                    if unboundaccount:
                        recipientaccount = unboundaccount
                    else:
                        continue
                make_ious.append(('transfer', recipientaccount))

            t.date = datetime.datetime.strptime(line[self.index['date']],
                                                '%Y-%m-%d')
            t.description = line[self.index['description']]
            t.original_description = line[self.index['description']]
            if line[self.index['status']] == 'Reconciled':
                t.validated = True

            t.save()

            if t:
                for thistag in make_categories:
                    cat = tags.get(thistag[0], None)
                    if not cat:
                        if createcategories:
                            cat = Category(owner=form.request.user,
                                           name=thistag[0])
                            cat.save()
                            tags[thistag[0]] = cat
                            tc = TransactionCategory(transaction=t,
                                                     category=cat,
                                                     amount=thistag[1])
                            tc.save()
                    else:
                        tc = TransactionCategory(transaction=t, category=cat,
                                                 amount=thistag[1])
                        tc.save()

                for i in make_ious:
                    if i[0] == 'iou':
                        i = IOU(owner=form.request.user, transaction=t,
                                recipient=i[1], amount=i[2],
                                money_transaction=i[3])
                        i.save()
                    elif i[0] == 'transfer':
                        rt = Transaction(account=i[1], date=t.date,
                                         description=t.description,
                                         amount=-t.amount,
                                         validated=t.validated)
                        rt.save()

                        i = IOU(owner=form.request.user, transaction=t,
                                recipient=form.request.user,
                                amount=abs(t.amount), money_transaction=True,
                                recipient_transaction=rt, accepted='a')
                        i.save()

        return ''
