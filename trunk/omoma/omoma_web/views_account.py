# Account views for Omoma
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

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.generic import list_detail

from omoma_web.forbidden import Forbidden
from omoma_web.models import Account, Transaction
from omoma_web.models import AccountForm
import settings


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
        aas = Account.objects.filter(pk=aid, owner=request.user)
        if aas:
            a = aas[0]
        else:
            return Forbidden()

    else:
        a = None

    if request.method == 'POST':

        form = AccountForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            form.instance.owner.add(request.user)
            if a:
                messages.info(request,
                       _('Account "%s" successfully modified') % form.instance)
            else:
                messages.info(request,
                        _('Account "%s" successfully created') % form.instance)
            return HttpResponseRedirect(reverse('accounts'))
    else:
        form = AccountForm(instance=a)

    return render_to_response('omoma_web/account.html', {
        'new': not aid,
        'title': _('Account "%s"') % a.name if a else _('New account'),
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
