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
IOU views for Omoma
"""
# pylint: disable=E1101

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.generic import list_detail

from omoma.omoma_web.forbidden import Forbidden
from omoma.omoma_web.models import IOU, Transaction, IOUForm
from omoma.omoma_web.transaction import TransactionForm


@login_required
def ious(request, recipient=None):
    """
    List IOUs
    """
    if recipient:
        rid = User.objects.get(username=recipient).id
        queryset = IOU.objects.filter(Q(recipient=rid) & Q(owner=request.user)|
                                      Q(recipient=request.user) & Q(owner=rid),
                                      accepted='a')
        title = _("IOUs for %s") % recipient
    else:
        queryset = IOU.objects.filter(Q(owner=request.user) & \
                                      ~Q(recipient=request.user) |
                                      Q(recipient=request.user) & \
                                      ~Q(owner=request.user),
                                      accepted='a')
        title = _("IOUs")
    return list_detail.object_list(request, template_object_name='iou',
                                   queryset=queryset, paginate_by=25,
                                   extra_context={'title':title,
                                                  'recipient':recipient})


# pylint: disable=R0912
@login_required
def iou(request, iid=None, tid=None, aid=None, rejected=False):
    """
    Configuration (or creation) view of an IOU
    """
    if iid:
        iis = IOU.objects.filter(pk=iid, owner=request.user)

        if iis:
            i = iis[0]
            title = _('IOU for "%s"') % i.transaction.description
        else:
            return Forbidden()

    elif tid:
        tts = Transaction.objects.filter(pk=tid, account__owner=request.user)

        if tts:
            i = IOU(transaction=tts[0], owner=request.user)
            title = _('New IOU for "%s"') % i.transaction.description
        else:
            return Forbidden()
    else:
        return Forbidden()

    if request.method == 'POST':
        form = IOUForm(request.POST, instance=i)

        if form.is_valid():
            # Verify the IOU links to a transaction the user owns
            if not request.user in form.instance.transaction.account.owner.all(): # pylint: disable=C0301
                return Forbidden()

            # Each time an IOU is modified, the recipient should accept again
            form.instance.accepted = 'p'
            form.instance.recipient_transaction = None
            form.save()

            if iid:
                messages.info(request,
                                 _('%s successfully modified') % form.instance)
            else:
                messages.info(request,
                                  _('%s successfully created') % form.instance)

            if tid:
                if aid:
                    target = reverse('transaction', kwargs={'aid':aid, 'tid':tid}) # pylint: disable=C0301
                else:
                    target = reverse('transaction', kwargs={'tid':tid})
            elif rejected:
                target = reverse('pending_ious')
            else:
                target = reverse('ious')
            return HttpResponseRedirect(target)
    else:
        form = IOUForm(instance=i)

    return render_to_response('omoma_web/iou.html', {
        'rejected': rejected,
        'tid': tid,
        'aid': aid,
        'new': not iid,
        'title': title,
        'form': form,
    }, RequestContext(request))


@login_required
def delete_iou(request, iid, tid=None, aid=None, rejected=False):
    """
    Delete an IOU
    """
    iis = IOU.objects.filter(pk=iid, owner=request.user)
    if iis:
        iname = unicode(iis[0])
        iis[0].delete()
        messages.info(request, _('%s successfully deleted') % iname)
        if rejected:
            target = reverse('pending_ious')
        elif tid:
            if aid:
                target = reverse('transaction', kwargs={'aid':aid, 'tid':tid})
            else:
                target = reverse('transaction', kwargs={'tid':tid})
        else:
            target = reverse('ious')
        return HttpResponseRedirect(target)
    else:
        return Forbidden()


@login_required
def accept_iou(request, iid):
    """
    Accept an IOU
    """
    iis = IOU.objects.filter(pk=iid, recipient=request.user)
    if iis:
        iis[0].accepted = 'a'
        iis[0].save()
        messages.info(request, _('%s successfully accepted') % iis[0])
    else:
        return Forbidden()
    return HttpResponseRedirect(reverse('pending_ious'))


@login_required
def accept_all_ious(request):
    """
    Accept all pending IOUs.

    (however, money transfers are not automatically attached)
    """
    iis = IOU.objects.filter(recipient=request.user, accepted='p',
                             money_transaction=False)
    number = len(iis)
    iis.update(accepted='a')
    messages.info(request, _('%d pending IOUs accepted' % number))
    return HttpResponseRedirect(reverse('pending_ious'))


@login_required
def attach_iou_to_transaction(request, iid, tid, aid=None, from_ious=False):
    """
    Attach an IOU to a recipient transaction
    """
    iis = IOU.objects.filter(pk=iid, recipient=request.user)
    tts = Transaction.objects.filter(pk=tid, account__owner=request.user)
    if not (iis and tts):
        return Forbidden()
    else:
        i = iis[0]
        i.recipient_transaction = tts[0]
        i.accepted = 'a'
        i.save()
        messages.info(request,
                    _('%(iou)s successfully attached to "%(transaction)s"') % {
                                                                  'iou':iis[0],
                                                         'transaction':tts[0]})
    if from_ious:
        target = reverse('pending_ious')
    elif aid:
        target = reverse('transaction', kwargs={'aid':aid, 'tid':tid})
    else:
        target = reverse('transaction', kwargs={'tid':tid})
    return HttpResponseRedirect(target)


@login_required
def detach_iou_from_transaction(request, tid, iid, aid=None):
    """
    Detach an IOU from its recipient transaction
    """
    iis = IOU.objects.filter(pk=iid,
                             recipient_transaction=tid,
                             recipient=request.user)
    tts = Transaction.object.filter(pk=tid,
                                    account__owner=request.user)

    if iis and tts:
        i = iis[0]
        i.recipient_transaction = None
        i.accepted = 'p'
        i.save()
        messages.info(request,
                  _('%(iou)s successfully detached from "%(transaction)s"') % {
                                                                  'iou':iis[0],
                                                         'transaction':tts[0]})

        if aid:
            target = reverse('transaction', kwargs={'aid':aid, 'tid':tid})
        else:
            target = reverse('transaction', kwargs={'tid':tid})
        return HttpResponseRedirect(target)

    else:
        return Forbidden()


@login_required
def attach_iou(request, iid):
    """
    Attach an IOU to a transaction
    """
    iis = IOU.objects.filter(pk=iid, recipient=request.user)
    if iis:
        i = iis[0]
        if not i.money_transaction:
            return Forbidden()
        if i.transaction.amount > 0:
            transamount = -i.amount
        else:
            transamount = i.amount
        transdesc = '%(owner)s: %(transaction)s' % {'owner':i.owner,
                                       'transaction':i.transaction.description}
        transactionobj = Transaction(date=i.transaction.date,
                                     amount=transamount,
                                     original_description=transdesc)
        newtransform = TransactionForm(request, instance=transactionobj)
        return render_to_response('attach_iou.html', {'iou':i,
                                               'transactionform': newtransform,
                                                    }, RequestContext(request))
    else:
        return Forbidden()


@login_required
def reject_iou(request, iid, pending=False):
    """
    Reject an IOU
    """
    iis = IOU.objects.filter(pk=iid, recipient=request.user)
    if iis:
        iis[0].accepted = 'r'
        iis[0].save()
        messages.info(request, _('%s successfully rejected') % iis[0])
    else:
        return Forbidden()
    if pending:
        target = reverse('pending_ious')
    else:
        target = reverse('ious')
    return HttpResponseRedirect(target)
