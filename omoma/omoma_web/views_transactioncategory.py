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
Transactioncategory views for Omoma
"""
# pylint: disable=E1101

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from omoma.omoma_web.forbidden import Forbidden
from omoma.omoma_web.models import Transaction, TransactionCategory
from omoma.omoma_web.models import TransactionCategoryForm


@login_required
def transactioncategory(request, tid, cid=None, aid=None):
    """
    Configuration (or creation) view of a link
    between a transaction and a category
    """
    if cid:
        tcs = TransactionCategory.objects.filter(transaction__exact=tid,
                                                 category__exact=cid,
                                      transaction__account__owner=request.user)
        if tcs:
            transactioncategoryobj = tcs[0]
        else:
            return Forbidden()

    else:
        tts = Transaction.objects.filter(pk=tid, account__owner=request.user)
        if tts:
            transactioncategoryobj = TransactionCategory(transaction=tts[0])
        else:
            return Forbidden()

    if request.method == 'POST':
        form = TransactionCategoryForm(request, request.POST,
                                       instance=transactioncategoryobj)
        if form.is_valid():

            # Validate the transaction and the category are owned by the user
            if not (form.instance.category.owner == request.user and
                request.user in form.instance.transaction.account.owner.all()):
                return Forbidden()

            form.save()

            if cid:
                messages.info(request,
   _('Category "%(category)s" successfully modified for "%(transaction)s"') % {
                                             'category':form.instance.category,
                                      'transaction':form.instance.transaction})
            else:
                messages.info(request,
    _('Category "%(category)s" successfully created for "%(transaction)s"') % {
                                             'category':form.instance.category,
                                      'transaction':form.instance.transaction})


            if aid:
                target = reverse('transaction', kwargs={'aid':aid, 'tid':tid})
            else:
                target = reverse('transaction', kwargs={'tid':tid})
            return HttpResponseRedirect(target)
    else:
        form = TransactionCategoryForm(request,
                                       instance=transactioncategoryobj)

    if transactioncategoryobj:
        title = _('Category for "%s"') % \
                                 transactioncategoryobj.transaction.description
    else:
        title = _('New category for "%s"') % \
                                 transactioncategoryobj.transaction.description

    return render_to_response('omoma_web/transactioncategory.html', {
        'aid': aid,
        'new': not cid,
        'title': title,
        'form': form,
    }, RequestContext(request))


@login_required
def delete_transactioncategory(request, tid, cid, aid=None):
    """
    Delete a link between a transaction and a category
    """
    tcs = TransactionCategory.objects.filter(transaction__exact=tid,
                                             category__exact=cid,
                                      transaction__account__owner=request.user)
    if tcs:
        transactionobj = tcs[0].transaction
        categoryobj = tcs[0].category
        tcs[0].delete()
        messages.info(request,
   _('Category "%(category)s" successfully deleted from "%(transaction)s"') % \
                                                {'category':categoryobj,
                                                 'transaction':transactionobj})
    else:
        return Forbidden()

    if aid:
        target = reverse('transaction', kwargs={'tid':tid, 'aid':aid})
    else:
        target = reverse('transaction', kwargs={'tid':tid})

    return HttpResponseRedirect(target)
