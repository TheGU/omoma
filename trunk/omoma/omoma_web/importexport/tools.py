# Import/export parsers for Omoma
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

import datetime

from django import forms
from django.contrib import messages
from django.utils.translation import ugettext as _

from omoma.omoma_web.models import Account, Transaction


class ImportForm(forms.Form):
    account = forms.ChoiceField()
    imported_file = forms.FileField(label=_('File to import'))

    def __init__(self, request, *args, **kwargs):
        aid = kwargs.pop('aid', None)
        super (ImportForm,self).__init__(*args, **kwargs)
        self.request = request
        self.fields['account'] = forms.ModelChoiceField(
                                    Account.objects.filter(owner=request.user),
                                                        initial=aid,
                                                        label=_('Account'))

    def clean(self):
        """
        Clean the form.

        When subclassed, you should use ::

            ImportForm.clean(self)

        ... before other verifications.
        """
        cleaned_data = self.cleaned_data

        if cleaned_data.get('imported_file').size > 1048576:

            msg = _('%s: the file is too large (max 1 MB).') % \
                                         cleaned_data.get('imported_file').name

            self._errors['imported_file'] = self.error_class([msg])
            del cleaned_data['imported_file']

        return cleaned_data

    def parse(self):
        """
        Parse the data

        Subclass this method.

        use "messages" to send messages to the user.

        return:

         * ``False`` if forbidden
         * a string, complementay information to display
        """
        return _('No parser defined for file %s.') % \
                                    self.cleaned_data.get('imported_file').name


def import_transaction(transaction):
    """
    Compare a transaction with existing transactions when importing,
    to import only transactions that were not imported in the past.
    Import transaction

    It compares :

     * account
     * amount
     * date
     * original description

    Return :

     * True: transaction is added
     * False: transaction already exists
     * None: error in transaction creation
    """
    account = transaction.account
    amount = transaction.amount
    date = transaction.date
    original_description = transaction.original_description

    tts = Transaction.objects.filter(date=date, amount=amount, account=account,
                                     original_description=original_description,
                                     deleted=False)
    if tts:
        return False
    else:
        try:
            transaction.save()
            return True
        except:
            return None
