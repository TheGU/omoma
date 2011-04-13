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
QIF import parser for Omoma
"""

import datetime

from django import forms
from django.utils.translation import ugettext as _

from omoma.omoma_web.importexport import import_transaction
from omoma.omoma_web.models import Account, Transaction

def name():
    """
    Return the parser's name
    """
    return 'QIF (Quicken Interchange Format)'


def check(filedata):
    """
    Check if the data fits to this parser
    """
    return filedata[:6] == '!Type:'


# pylint: disable=E1101,W0232,R0903
class DetailsForm(forms.Form):
    """
    QIF details form
    """
    account = forms.ChoiceField()
    QIF_DATE_FORMATS = (
        ('%d/%m/%y', _('DD/MM/YY')),
        ('%m/%d/%y', _('MM/DD/YY')),
        ('%d/%m/%Y', _('DD/MM/YYYY')),
        ('%m/%d/%Y', _('MM/DD/YYYY')),
        ('%Y-%m-%d', _('YYYY-MM-DD')),
    )
    date_format = forms.ChoiceField(QIF_DATE_FORMATS,
                                    label=_('Date format'))

    # pylint: disable=E1002
    def __init__(self, request, *args, **kwargs):
        aid = kwargs.pop('aid', None)
        super (DetailsForm, self).__init__(*args, **kwargs)
        self.request = request
        self.fields['account'] = forms.ModelChoiceField(
                                    Account.objects.filter(owner=request.user),
                                                        initial=aid,
                                                        label=_('Account'))


class Parser:
    """
    The parser
    """

    def __init__(self, filedata):
        self.filedata = filedata

    def parse(self, form):
        """
        Parse a QIF file.

        Tested and validated with a QIF file from the Credit Mutuel french bank
        """
        account = form.cleaned_data.get('account')
        dateformat = form.cleaned_data.get('date_format')

        # Validate the account is owned by the user
        if not form.request.user in account.owner.all():
            return False

        transactions_added = 0
        transactions_already_exist = 0
        transactions_failed = 0

        transaction = Transaction(account=account)
        for line in self.filedata.split('\n')[1:]:
            if line:
                if line.strip() == '^':
                    result = import_transaction(form.request, transaction)
                    if result == True:
                        transactions_added = transactions_added + 1
                    elif result == False:
                        transactions_already_exist = \
                                                 transactions_already_exist + 1
                    elif result == None:
                        transactions_failed = transactions_failed + 1

                    transaction = Transaction(account=account)
                elif line[0] == 'D':
                    transaction.date = datetime.datetime.strptime(\
                                                  line[1:].strip(), dateformat)
                elif line[0] == 'T':
                    transaction.amount = line[1:].strip().replace(',', '')
                elif line[0] == 'P':
                    descr = line[1:].strip()
                    transaction.original_description = descr

        msg = []
        if transactions_added:
            msg.append(_('%d transactions imported.') % \
                                                    transactions_added)
        if transactions_already_exist:
            msg.append(_('%d transactions already existed.') % \
                                            transactions_already_exist)
        if transactions_failed:
            msg.append(_('Failed to add %d transactions.') % \
                                                   transactions_failed)
        return ' '.join(msg)
