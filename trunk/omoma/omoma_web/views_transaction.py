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
Transaction views from Omoma
"""
# pylint: disable=E1101

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.generic import list_detail

from omoma.omoma_web.forbidden import Forbidden
from omoma.omoma_web.models import Account, IOU, Transaction
from omoma.omoma_web.transaction import TransactionForm


@login_required
def transactions(request, aid=None, deleted=False):
    """
    List transactions
    """
    if deleted:
        queryset = Transaction.objects.filter(account__owner=request.user,
                                              deleted=True)
        title = _('Deleted transactions')
    elif aid:
        aas = Account.objects.filter(pk=aid, owner=request.user)
        if not aas:
            return Forbidden()
        queryset = Transaction.objects.filter(account=aid, deleted=False)
        title = _('Transactions for %s') % aas[0].name
    else:
        aid = False
        queryset = Transaction.objects.filter(account__owner=request.user,
                                              deleted=False)
        title = _("Transactions")

    return list_detail.object_list(request, template_object_name='transaction',
                                   queryset=queryset, paginate_by=50,
                                   extra_context={'title':title,
                                                  'aid':aid,
                                                  'deleted':deleted})


@login_required
def transaction(request, tid=None, iid=None, aid=None):
    """
    Configuration (or creation) view of a transaction
    """
    if tid:
        transactionslist = Transaction.objects.filter(pk=tid,
                                                   account__owner=request.user)
        if transactionslist:
            transactionobj = transactionslist[0]
        else:
            return Forbidden()

    else:
        transactionobj = None

    if request.method == 'POST':
        form = TransactionForm(request, request.POST, instance=transactionobj)
        if form.is_valid():
            # Validate the account is owned by the user
            if not request.user in form.cleaned_data['account'].owner.all():
                return Forbidden()

            form.save()

            if transactionobj:
                messages.info(request,
                   _('Transaction "%s" successfully modified') % form.instance)
            else:
                messages.info(request,
                    _('Transaction "%s" successfully created') % form.instance)

            if iid:
                i = IOU.objects.get(pk=iid)
                i.recipient_transaction = form.instance
                i.accepted = 'a'
                i.save()

            if iid:
                target = reverse('iou', kwargs={'iid':iid})
            elif aid:
                target = reverse('transactions', kwargs={'aid':aid})
            else:
                target = reverse('transactions')
            return HttpResponseRedirect(target)

    else:
        form = TransactionForm(request, instance=transactionobj)

    return render_to_response('omoma_web/transaction.html', {
        'iid': iid,
        'aid': aid,
        'new': not tid,
        'title': _('Transaction "%s"') % transactionobj.description \
                 if transactionobj else _('New transaction'),
        'form': form,
    }, RequestContext(request))


@login_required
def delete_transaction(request, tid, aid=None, restore=False):
    """
    Delete a transaction
    """
    transactionslist = Transaction.objects.filter(pk=tid,
                                                  account__owner=request.user)
    if transactionslist:
        transactionobj = transactionslist[0]
    else:
        return Forbidden()

    iis = IOU.objects.filter(Q(transaction=transactionobj) |
                             Q(recipient_transaction=transactionobj))
    for i in iis:
        i.accepted = 'p'
        i.save()

    transactionobj.deleted = not transactionobj.deleted
    transactionobj.validates = False
    transactionobj.save()

    if restore:
        messages.info(request,
                  _('Transaction "%s" successfully restored') % transactionobj)
        target = reverse('deleted_transactions')
    else:
        messages.info(request,
                   _('Transaction "%s" successfully deleted') % transactionobj)
        if aid:
            target = reverse('transactions', kwargs={'aid':aid})
        else:
            target = reverse('transactions')
    return HttpResponseRedirect(target)


@login_required
def validate_transaction(request, tid, aid=None):
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
    if aid:
        target = reverse('transactions', kwargs={'aid':aid})
    else:
        target = reverse('transactions')
    return HttpResponseRedirect(target)


@login_required
def remove_deleted_transactions(request):
    """
    Remove all deleted transactions
    """
    if request.method == 'POST':
        Transaction.objects.filter(account__owner=request.user,
                                   deleted=True).delete()

        messages.info(request, _('Successfully removed deleted transactions'))
        return HttpResponseRedirect(reverse('transactions'))

    else:
        return render_to_response('omoma_web/transactions_confirm_delete.html',
                                  context_instance=RequestContext(request))
