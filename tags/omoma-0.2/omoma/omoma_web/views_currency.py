# Copyright 2011 Alin Voinea
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
""" Currency views for Omoma
"""
from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.generic import list_detail
from omoma_web.forbidden import Forbidden
from omoma_web.models import Currency, CurrencyForm

@login_required
def currencies(request):
    """
    List currencies
    """
    return list_detail.object_list(request, template_object_name='currency',
                                   queryset=Currency.objects.all())

@permission_required("omoma_web.add_currency")
def currency(request, cid=None):
    """
    Configuration (or creation) view of a currency
    """
    if cid:
        ccy = Currency.objects.filter(pk=cid)
        if ccy:
            ccy = ccy[0]
        else:
            return Forbidden()

    else:
        ccy = Currency()

    if request.method == 'POST':

        form = CurrencyForm(request.POST, instance=ccy)
        if form.is_valid():
            form.save()
            if cid:
                messages.info(request,
                      _('Currency "%s" successfully modified') % form.instance)
            else:
                messages.info(request,
                       _('Currency "%s" successfully created') % form.instance)
            return HttpResponseRedirect(reverse('currencies'))

    else:
        form = CurrencyForm(instance=ccy)

    return render_to_response('omoma_web/currency.html', {
        'new': not cid,
        'title': _(
            'Currency "%s"') % ccy.name if cid else _('New currency'),
        'form': form,
    }, RequestContext(request))

@permission_required("omoma_web.delete_currency")
def delete_currency(request, cid):
    """
    Delete a currency
    """
    ccs = Currency.objects.filter(pk=cid)
    if not ccs:
        return Forbidden()

    ccs = ccs[0]
    if ccs.used:
        return Forbidden()

    if request.method == 'POST':
        cname = unicode(ccs.name)
        ccs.delete()
        messages.info(request, _('Currency "%s" successfully deleted') % cname)
        return HttpResponseRedirect(reverse('currencies'))
    else:
        return render_to_response('omoma_web/currency_confirm_delete.html',
                                  {'currency': ccs}, RequestContext(request))
