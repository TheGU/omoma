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
Import views for Omoma
"""

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from omoma.omoma_web.forbidden import Forbidden
from omoma.omoma_web.importexport import guessparser, listparsers


# pylint: disable=E1101,W0232,R0903
class ImportForm(forms.Form):
    """
    Generic importation form
    """
    imported_file = forms.FileField(label=_('File to import'))
    filecontent = None
    fileparser = None

    def clean(self):
        """
        Clean the form.
        """
        cleaned_data = self.cleaned_data
        impfile = cleaned_data.get('imported_file')
        if impfile.size > 1048576:
            msg = _('%s: the file is too large (max 1 MB).') % impfile.name
            self._errors['imported_file'] = self.error_class([msg])
            del cleaned_data['imported_file']
        else:
            self.filecontent = impfile.read()
            self.fileparser = guessparser(self.filecontent)
            if not self.fileparser:
                msg = _('%s: this file format is not known.') % impfile.name
                self._errors['imported_file'] = self.error_class([msg])
                del cleaned_data['imported_file']
        return cleaned_data


@login_required
def import_transactions(request, aid=None):
    """
    Import transactions
    """
    if request.session.has_key('importparser'):
        details = True
        instructions = request.session['importparser']['instructions']
        supported_formats = None

        # A file has already been selected and uploaded, a parser is defined
        if request.method == 'POST':
            form = request.session['importparser']['form'](request,
                                                           request.POST,
                                                           aid=aid)
            if form.is_valid():
                message = request.session['importparser']['parser'].parse(form)
                if message is False:
                    return Forbidden()

                msg = ' '.join([_("Successfully imported transactions."),
                                message])
                messages.info(request, msg)
                del request.session['importparser']
                if aid:
                    return HttpResponseRedirect(reverse('transactions',
                                                        kwargs={'aid':aid}))
                else:
                    return HttpResponseRedirect(reverse('transactions'))

        else:
            form = request.session['importparser']['form'](request, aid=aid)

    else:
        details = False
        instructions = False
        supported_formats = listparsers()

        # No file uploaded yet
        if request.method == 'POST':
            form = ImportForm(request.POST, request.FILES)
            if form.is_valid():
                request.session['importparser'] = form.fileparser
                if aid:
                    return HttpResponseRedirect(reverse('import_transactions',
                                                        kwargs={'aid':aid}))
                else:
                    return HttpResponseRedirect(reverse('import_transactions'))

        else:
            form = ImportForm()

    return render_to_response('import_transactions.html', {
        'form': form,
        'aid': aid,
        'details': details,
        'instructions': instructions,
        'supported_formats':supported_formats,
    }, RequestContext(request))


@login_required
def cancel_import_transactions(request, aid=None):
    """
    Cancel transactions importation
    """
    del request.session['importparser']
    if aid:
        return HttpResponseRedirect(reverse('import_transactions',
                                            kwargs={'aid':aid}))
    else:
        return HttpResponseRedirect(reverse('import_transactions'))
