# Import views for Omoma
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
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from omoma_web.forbidden import Forbidden
from omoma_web.importexport import supported_formats


@login_required
def choose_format(request, aid=None):
    """
    File format choice view
    """
    return render_to_response('choose_import_format.html', {
        'formats':supported_formats,
        'aid': aid,
    }, RequestContext(request))


def import_transactions(request, format=None, aid=None):
    """
    Transactions import view
    """
    error = None
    if request.method == 'POST':
        form = supported_formats[format]['form'](request, request.POST,
                                                 request.FILES, aid=aid)
        if form.is_valid():
            parse_response = form.parse()
            if parse_response:
                msg = ' '.join([_("Successfully imported transactions."),
                                parse_response])
                messages.info(request, msg)
                if aid:
                    return HttpResponseRedirect(reverse('transactions',
                                                           kwargs={'aid':aid}))
                else:
                    return HttpResponseRedirect(reverse('transactions'))
            else:
                return Forbidden()


    else:
        form = supported_formats[format]['form'](request, aid=aid)

    return render_to_response('import_transactions.html', {
        'aid': aid,
        'form': form,
    }, RequestContext(request))
