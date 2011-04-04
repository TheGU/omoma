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
Account views for Omoma
"""
# pylint: disable=E1101

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.generic import list_detail

from omoma.omoma_web.forbidden import Forbidden
from omoma.omoma_web.models import Account
from omoma.omoma_web.models import AccountForm


@login_required
def accounts(request):
    """
    List accounts
    """
    return list_detail.object_list(request, template_object_name='account',
                           queryset=Account.objects.filter(owner=request.user))


@login_required
def account(request, aid=None):
    """
    Configuration (or creation) view of an account
    """
    if aid:
        accountslist = Account.objects.filter(pk=aid, owner=request.user)
        if accountslist:
            accountobj = accountslist[0]
        else:
            return Forbidden()

    else:
        accountobj = None

    if request.method == 'POST':

        form = AccountForm(request.POST, instance=accountobj)
        if form.is_valid():
            form.save()
            form.instance.owner.add(request.user)
            if accountobj:
                messages.info(request,
                       _('Account "%s" successfully modified') % form.instance)
            else:
                messages.info(request,
                        _('Account "%s" successfully created') % form.instance)
            return HttpResponseRedirect(reverse('accounts'))
    else:
        form = AccountForm(instance=accountobj)

    return render_to_response('omoma_web/account.html', {
        'new': not aid,
        'title': _('Account "%s"') % accountobj.name if accountobj \
                 else _('New account'),
        'form': form,
    }, RequestContext(request))


@login_required
def delete_account(request, aid):
    """
    Delete an account
    """
    aas = Account.objects.filter(pk=aid, owner=request.user)
    if not aas:
        return Forbidden()

    if request.method == 'POST':
        aname = unicode(aas[0])
        aas[0].delete()
        messages.info(request, _('Account "%s" successfully deleted') % aname)
        return HttpResponseRedirect(reverse('accounts'))

    else:
        return render_to_response('omoma_web/account_confirm_delete.html',
                                   {'account':aas[0]}, RequestContext(request))
