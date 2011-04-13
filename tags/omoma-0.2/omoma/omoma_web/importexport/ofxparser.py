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
OFX import parser for Omoma
"""
#  Uses the ofx2qif program (shipped with libofx)

import datetime
import os
import subprocess
import tempfile

from django import forms
from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from omoma.omoma_web.importexport import import_transaction
from omoma.omoma_web.models import Account, Transaction

def name():
    """
    Return the parser's name
    """
    if os.access(settings.OFX2QIF, os.X_OK):
        return 'OFX (Open Financial Exchange)'
    else:
        return None


def check(filedata):
    """
    Check if the data fits to this parser
    """
    tmpfile, tmpfilename = tempfile.mkstemp('.tmp', 'omoma-ofx-import-')
    os.write(tmpfile, filedata)
    os.close(tmpfile)
    qif = subprocess.Popen([settings.OFX2QIF, tmpfilename],
                           stdout=subprocess.PIPE).stdout.read()
    os.remove(tmpfilename)
    # Return True if there is content in "qif"
    return not not qif


# pylint: disable=E1101,W0232,R0903
class DetailsForm(forms.Form):
    """
    OFX details form
    """

    # pylint: disable=E1002
    def __init__(self, request, *args, **kwargs):
        aid = kwargs.pop('aid', None)
        super (DetailsForm, self).__init__(*args, **kwargs)
        self.request = request
        for account in request.session['importparser']['parser'].accounts():
            self.fields['account%s' % slugify(account)] = \
                                                        forms.ModelChoiceField(
                                    Account.objects.filter(owner=request.user),
                                                   initial=aid, required=False,
                                             label=_('Account "%s"') % account)


class Parser:
    """
    The parser
    """

    def __init__(self, filedata):
        tmpfile, tmpfilename = tempfile.mkstemp('.tmp', 'omoma-ofx-import-')
        os.write(tmpfile, filedata)
        os.close(tmpfile)
        self.qif = subprocess.Popen([settings.OFX2QIF, tmpfilename],
                                    stdout=subprocess.PIPE).stdout.read()
        os.remove(tmpfilename)

    def accounts(self):
        """
        Return the list of all accounts
        """
        accounts = []
        for line in self.qif.split('\n'):
            if line == '!Account':
                inaccount = True
                accountname = None
            elif line == '^' and inaccount:
                accounts.append(accountname)
                inaccount = False
            elif line.startswith('N') and inaccount:
                accountname = line[1:]
        return accounts

    def parse(self, form):
        """
        Parse an OFX file.

        Tested with files from :
         - Credit Mutuel (french bank)
         - La Banque Postale (french bank)
        """
        accounts = {}
        for field in form.fields.keys():
            if field.startswith('account'):
                act = form.cleaned_data.get(field)
                if act:
                    # Validate the accounts are owned by the user
                    if not form.request.user in act.owner.all():
                        return False
                    accounts[field[7:]] = act

        msg = []

        inaccount = False
        account = None
        transactions_added = 0
        transactions_already_exist = 0
        transactions_failed = 0
        for line in self.qif.split('\n'):
            if line:
                if line == '!Account':
                    if account:
                        details = []
                        if transactions_added:
                            details.append(_('%d imported') % \
                                                            transactions_added)
                        if transactions_already_exist:
                            details.append(_('%d already existed') % \
                                                    transactions_already_exist)
                        if transactions_failed:
                            details.append(_('%d failed' % \
                                                          transactions_failed))
                        msg.append(_('In account "%(account)s": %(details)s.')\
                                              % {'account':account.name,
                                                 'details':', '.join(details)})
                    inaccount = True
                    accountname = ''
                    account = None
                    transactions_added = 0
                    transactions_already_exist = 0
                    transactions_failed = 0
                if inaccount and line[0] == 'N':
                    accountname = line[1:]
                    if accounts.has_key(slugify(accountname)):
                        account = accounts[slugify(accountname)]
                if line.startswith('!Type:') and account:
                    transaction = Transaction(account=account)
                elif line == '^':
                    if inaccount:
                        inaccount = False
                    elif account:
                        result = import_transaction(form.request, transaction)
                        if result == True:
                            transactions_added = transactions_added + 1
                        elif result == False:
                            transactions_already_exist = \
                                                 transactions_already_exist + 1
                        elif result == None:
                            transactions_failed = transactions_failed + 1
                        transaction = Transaction(account=account)

                elif line[0] == 'D' and not inaccount:
                    transaction.date = datetime.datetime.strptime(\
                                                  line[1:].strip(), '%d/%m/%Y')
                elif line[0] == 'T' and not inaccount:
                    transaction.amount = line[1:]
                elif line[0] == 'P' and not inaccount:
                    description = line[1:].strip()
                    transaction.original_description = description

        return ''.join(msg)
