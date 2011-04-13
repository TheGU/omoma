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
User preferences and configuration views for Omoma
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from omoma.omoma_web.models import Transaction, TransactionCategory
from omoma.omoma_web.models import AutomaticCategory, AutomaticCategoryForm
from omoma.omoma_web.models import TransactionRenaming, TransactionRenamingForm

@login_required
def automaticrules(request):
    """
    List automatic transaction renaming and category assignation rules
    """

    renaming = TransactionRenaming.objects.filter(owner=request.user)
    category = AutomaticCategory.objects.filter(category__owner=request.user)


    return render_to_response('automaticrules.html', {
        'renamings': renaming,
        'categories': category,
    }, RequestContext(request))


@login_required
def automaticcategory(request, acid=None):
    """
    Configuration (or creation) view of an automatic category assignment
    """
    if acid:
        ruleslist = AutomaticCategory.objects.filter(pk=acid,
                                                     category__owner=request.user)
        if ruleslist:
            ruleobj = ruleslist[0]
        else:
            return Forbidden()
    else:
        ruleobj = None

    if request.method == 'POST':
        form = AutomaticCategoryForm(request, request.POST, instance=ruleobj)
        if form.is_valid():
            # Validate the category is owned by the user
            if form.cleaned_data['category'].owner != request.user:
                return Forbidden()

            form.save()

            if ruleobj:
                messages.info(request,
                   _('%s successfully modified') % form.instance)
            else:
                messages.info(request,
                    _('%s successfully created') % form.instance)

            return HttpResponseRedirect(reverse('automaticrules'))

    else:
        form = AutomaticCategoryForm(request, instance=ruleobj)

    return render_to_response('omoma_web/automaticcategory.html', {
        'new': not acid,
        'title': ruleobj,
        'form': form,
    }, RequestContext(request))



@login_required
def transactionrenaming(request, trid=None):
    """
    Configuration (or creation) view of an automatic transaction renaming
    """
    if trid:
        ruleslist = TransactionRenaming.objects.filter(pk=trid,
                                                       owner=request.user)
        if ruleslist:
            ruleobj = ruleslist[0]
        else:
            return Forbidden()
    else:
        ruleobj = None

    if request.method == 'POST':
        form = TransactionRenamingForm(request.POST, instance=ruleobj)
        if form.is_valid():

            form.save()

            if ruleobj:
                messages.info(request,
                   _('%s successfully modified') % form.instance)
            else:
                messages.info(request,
                    _('%s successfully created') % form.instance)

            return HttpResponseRedirect(reverse('automaticrules'))

    else:
        form = TransactionRenamingForm(instance=ruleobj)

    return render_to_response('omoma_web/transactionrenaming.html', {
        'new': not trid,
        'title': ruleobj,
        'form': form,
    }, RequestContext(request))


@login_required
def apply_automaticcategory(request, acid):
    """
    Apply a transaction renaming rule to existing transactions
    """
    ruleslist = AutomaticCategory.objects.filter(pk=acid,
                                                 category__owner=request.user)
    if ruleslist:
        ruleobj = ruleslist[0]
    else:
        return Forbidden()

    if request.method == 'POST':
        selected = request.POST.getlist('applyto')
        if len(selected):
            for transactionid in selected:
                trans = Transaction.objects.get(id=transactionid,
                                                account__owner=request.user)
                TransactionCategory(transaction=trans,
                                    category=ruleobj.category).save()
            messages.info(request,
                      _('The category has been applied to %d transactions') % \
                                                                 len(selected))
            return HttpResponseRedirect(reverse('automaticrules'))
        else:
            messages.info(request,
                    _('The category has not been applied to any transaction.'))

    alltransactions = Transaction.objects.filter(description__icontains= \
                                                 ruleobj.description)
    transactions = []
    for trans in alltransactions:
        if not trans.transactioncategory_set.all():
            transactions.append(trans)

    return render_to_response('omoma_web/apply_automaticcategory.html', {
        'title': unicode(ruleobj),
        'transactions': transactions,
    }, RequestContext(request))


@login_required
def apply_transactionrenaming(request, trid):
    """
    Apply a transaction renaming rule to existing transactions
    """
    ruleslist = TransactionRenaming.objects.filter(pk=trid,
                                                   owner=request.user)
    if ruleslist:
        ruleobj = ruleslist[0]
    else:
        return Forbidden()

    if request.method == 'POST':
        selected = request.POST.getlist('applyto')
        if len(selected):
            for transactionid in selected:
                trans = Transaction.objects.get(id=transactionid,
                                                account__owner=request.user)
                trans.description = ruleobj.target_description
                trans.save()
            messages.info(request, _('%d transactions renamed.')%len(selected))
            return HttpResponseRedirect(reverse('automaticrules'))
        else:
            messages.info(request,
                    _('No transaction has been renamed.'))

    transactions = Transaction.objects.filter(
            Q(original_description__icontains=ruleobj.original_description) & \
                                    ~Q(description=ruleobj.target_description))

    return render_to_response('omoma_web/apply_transactionrenaming.html', {
        'title': unicode(ruleobj),
        'transactions': transactions,
    }, RequestContext(request))


@login_required
def delete_automaticcategory(request, acid):
    """
    Delete a transaction renaming rule
    """
    ruleslist = AutomaticCategory.objects.filter(pk=acid,
                                                 category__owner=request.user)
    if ruleslist:
        rname = unicode(ruleslist[0])
        ruleslist[0].delete()
        messages.info(request, _('%s successfully deleted') % rname)
        return HttpResponseRedirect(reverse('automaticrules'))
    else:
        return Forbidden()


@login_required
def delete_transactionrenaming(request, trid):
    """
    Delete a transaction renaming rule
    """
    ruleslist = TransactionRenaming.objects.filter(pk=trid,
                                                   owner=request.user)
    if ruleslist:
        rname = unicode(ruleslist[0])
        ruleslist[0].delete()
        messages.info(request, _('%s successfully deleted') % rname)
        return HttpResponseRedirect(reverse('automaticrules'))
    else:
        return Forbidden()
