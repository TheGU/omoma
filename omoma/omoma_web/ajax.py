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
Account API access for Omoma
"""

import simplejson as json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from omoma.omoma_web.templatetags import omoma as tags
from omoma.omoma_web.models import Account, IOU, Transaction
from omoma.omoma_web.transaction import AjaxTransactionForm


@login_required
def accounts_balances(request):
    """
    Accounts balances
    """
    accountslist = Account.objects.filter(owner=request.user)

    accountsjson = {}
    for account in accountslist:
        accid = account.id
        accvalbal = tags.signedmoney(account.validated_balance(), account)
        acccurbal = tags.signedmoney(account.current_balance(), account)
        accountsjson[accid] = {'validated': accvalbal, 'current': acccurbal}
    return HttpResponse(json.dumps(accountsjson))


@login_required
def validate_transaction(request, tid):
    """
    Validate a transaction
    """
    transactionslist = Transaction.objects.filter(pk=tid,
                                                  account__owner=request.user)
    if transactionslist:
        transactionobj = transactionslist[0]
    else:
        return Forbidden()

    transactionobj.validated = not transactionobj.validated
    transactionobj.save()

    serializer = serializers.get_serializer("json")()
    serializer.serialize((transactionobj,), ensure_ascii=False)
    return HttpResponse(serializer.getvalue())


@login_required
def delete_transaction(request, tid):
    """
    Delete a transaction
    """
    transactionslist = Transaction.objects.filter(pk=tid,
                                                  account__owner=request.user)
    if transactionslist:
        transactionobj = transactionslist[0]
    else:
        return Forbidden()

    IOU.objects.filter(transaction=transactionobj).delete()
    iis = IOU.objects.filter(recipient_transaction=transactionobj)
    for i in iis:
        i.accepted = 'p'
        i.save()

    transactionobj.deleted = True
    transactionobj.save()

    messages.info(request,
               _('Transaction "%s" successfully deleted') % transactionobj)
    return HttpResponse('OK')

def edit_transaction(request, tid):
    """
    Edit a transaction
    """
    transactionslist = Transaction.objects.filter(pk=tid,
                                                  account__owner=request.user)
    if transactionslist:
        transactionobj = transactionslist[0]
    else:
        return Forbidden()

    form = AjaxTransactionForm(request, instance=transactionobj)

    return render_to_response('ajax/edited_row.html', {
        't':transactionobj,
        'form':form
    }, RequestContext(request))

def apply_edit_transaction(request, tid):
    """
    Cancel the edition of a transaction
    """
    transactionslist = Transaction.objects.filter(pk=tid,
                                                  account__owner=request.user)
    if transactionslist:
        transactionobj = transactionslist[0]
    else:
        return Forbidden()

    if request.method == 'POST':

        form = AjaxTransactionForm(request, request.POST, instance=transactionobj)
        if form.is_valid():
            # Validate the account is owned by the user
            if not request.user in form.cleaned_data['account'].owner.all():
                return Forbidden()

            form.save()

            messages.info(request, _('Transaction "%s" successfully modified') % form.instance)

    return render_to_response('ajax/regular_row.html', {
        't':transactionobj,
    }, RequestContext(request))

def cancel_edit_transaction(request, tid):
    """
    Cancel the edition of a transaction
    """
    transactionslist = Transaction.objects.filter(pk=tid,
                                                  account__owner=request.user)
    if transactionslist:
        transactionobj = transactionslist[0]
    else:
        return Forbidden()

    return render_to_response('ajax/regular_row.html', {
        't':transactionobj,
    }, RequestContext(request))
