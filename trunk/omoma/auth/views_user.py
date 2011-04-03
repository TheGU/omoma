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
""" User views for Omoma
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
from auth.user import User, UserForm

@login_required
def users(request):
    """
    List users
    """
    return list_detail.object_list(request, template_object_name='user',
                                   queryset=User.objects.filter())

@permission_required("auth.add_user")
def user(request, cid=None):
    """
    Configuration (or creation) view of a user
    """
    if cid:
        current_user = User.objects.filter(pk=cid)
        if user:
            current_user = current_user[0]
        else:
            return Forbidden()
    else:
        current_user = User()

    if request.method == 'POST':

        form = UserForm(request.POST, instance=current_user)
        if form.is_valid():
            form.save()
            if cid:
                messages.info(request,
                      _('User "%s" successfully modified') % form.instance)
            else:
                messages.info(request,
                       _('User "%s" successfully created') % form.instance)
            return HttpResponseRedirect(reverse('users'))

    else:
        form = UserForm(instance=current_user)

    return render_to_response('auth/user.html', {
        'new': not cid,
        'title': _(
            'User "%s"') % current_user.username if cid else _('New user'),
        'form': form,
    }, RequestContext(request))

@permission_required("auth.delete_user")
def delete_user(request, cid):
    """
    Delete a user
    """
    current_user = User.objects.filter(pk=cid)
    if not current_user:
        return Forbidden()

    current_user = current_user[0]
    if request.method == 'POST':
        cname = unicode(current_user)
        current_user.delete()
        messages.info(request, _('User "%s" successfully deleted') % cname)
        return HttpResponseRedirect(reverse('users'))
    else:
        return render_to_response(
            'auth/user_confirm_delete.html', {'user': current_user},
            RequestContext(request))
