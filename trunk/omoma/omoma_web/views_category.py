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
Category views for Omoma
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
from omoma.omoma_web.models import Category, CategoryForm

@login_required
def categories(request):
    """
    List categories
    """
    return list_detail.object_list(request, template_object_name='category',
                          queryset=Category.objects.filter(owner=request.user))

@login_required
def category(request, cid=None):
    """
    Configuration (or creation) view of a category
    """
    if cid:
        categorieslist = Category.objects.filter(pk=cid, owner=request.user)
        if categorieslist:
            categoryobj = categorieslist[0]
        else:
            return Forbidden()

    else:
        categoryobj = Category(owner=request.user)

    if request.method == 'POST':

        form = CategoryForm(request, request.POST, instance=categoryobj)
        if form.is_valid():

            if form.instance.owner != request.user:
                return Forbidden()

            if form.instance.parent and \
               form.instance.parent.owner != request.user:
                return Forbidden()

            form.save()
            if cid:
                messages.info(request,
                      _('Category "%s" successfully modified') % form.instance)
            else:
                messages.info(request,
                       _('Category "%s" successfully created') % form.instance)
            return HttpResponseRedirect(reverse('categories'))

    else:
        form = CategoryForm(request, instance=categoryobj)

    return render_to_response('omoma_web/category.html', {
        'new': not cid,
        'title': _('Category "%s"') % categoryobj.name if cid \
                 else _('New category'),
        'form': form,
    }, RequestContext(request))

@login_required
def delete_category(request, cid):
    """
    Delete a category
    """
    ccs = Category.objects.filter(pk=cid, owner=request.user)
    if not ccs:
        return Forbidden()

    if request.method == 'POST':
        cname = unicode(ccs[0])
        ccs[0].delete()
        messages.info(request, _('Category "%s" successfully deleted') % cname)
        return HttpResponseRedirect(reverse('categories'))

    else:
        return render_to_response('omoma_web/category_confirm_delete.html',
                                  {'category':ccs[0]}, RequestContext(request))
