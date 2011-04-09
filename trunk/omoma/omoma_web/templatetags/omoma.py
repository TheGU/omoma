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
Django template tags and filters for Omoma
"""
# pylint: disable=E1101

import datetime

from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from omoma_web.models import Account, IOU, Transaction

# pylint: disable=C0103
register = template.Library()


def do_categorytree(parser, token):
    """
    Display a HTML list tree of a category and its children

    Usage::

        {% categorytree category %}

    """
    class CategoryTreeParser(template.Node):
        """
        Make a tree out of the categories list
        """
        def __init__(self, category):
            super(CategoryTreeParser, self).__init__()
            self.category = category

        def rendercategory(self, category):
            """
            Render a category and its subcategories
            """
            html = []

            subcategories = category.category_set.all()

            if subcategories:
                html.append('<ul>')
                for subcat in subcategories:
                    html.append('<li>%s (%d transactions)</li>' % (subcat.name,
                                                  subcat.count_transactions()))
                    html.append(self.rendercategory(subcat))
                html.append('</ul>')

            return ''.join(html)

        def render(self, context):
            cat = self.category.resolve(context)
            return self.rendercategory(cat)

    contents = token.split_contents()
    return CategoryTreeParser(parser.compile_filter(contents[1]))


def do_contentbox(parser, token):
    """
    Create a box

    Usage::

        {% contentbox %}
            Some content...
        {% endbox %}
    """
    class ContentboxParser(template.Node):
        """
        Create a box with <div> elements
        """
        def __init__(self, nodelist, title=None):
            super(ContentboxParser, self).__init__()
            self.title = title
            self.nodelist = nodelist

        def render(self, context):
            boxcontent = ['<div class="box">']
            if self.title:
                boxcontent.append('<h2 class="title">%s</h2>' %
                                                   self.title.resolve(context))
            boxcontent.append('<div class="content">')
            boxcontent.append(self.nodelist.render(context))
            boxcontent.append('</div></div>')
            return ''.join(boxcontent)

    nodelist = parser.parse(('endbox',))
    parser.delete_first_token()

    contents = token.split_contents()
    if len(contents) > 1:
        return ContentboxParser(nodelist, parser.compile_filter(contents[1]))
    else:
        return ContentboxParser(nodelist)


# pylint: disable=W0613
def do_get_accounts_list(parser, token):
    """
    Set the "accountslist" var to the list of accounts

    Usage::

        {% getaccountslist %}

        <ul>
        {% for account in accountslist %}
            <li>{{ account.name }}</li>
        {% endfor %}
        </ul>
    """

    class AccountsListNode(template.Node):
        """
        Create the accounts list
        """
        def render(self, context):
            userid = context['request'].user.id
            context['accountslist'] = Account.objects.filter(owner=userid)
            return ''

    return AccountsListNode()

# pylint: disable=W0613
def do_get_iou_peers_list(parser, token):
    """
    Set the "ioupeerslist" var to the list of debtors and creditors

    Usage::

        {% getioupeerslist %}

        <ul>
        {% for peer in ioupeerslist %}
            <li>{{ peer.id }}, {{ peer.name }},
                {{ peer.type }}, {{ peer.amount }}</li>
        {% endfor %}
        </ul>
    """
    class IOUPeersListNode(template.Node):
        """
        Create a list of IOU peers
        """
        def render(self, context):
            user = context['request'].user

            i_gave_to_peers = IOU.objects.filter(owner=user, accepted='a',
                                                 transaction__amount__lt=0)

            i_received_from_peers = IOU.objects.filter(owner=user,
                                                       accepted='a',
                                                     transaction__amount__gt=0)

            peers_gave_to_me = IOU.objects.filter(recipient=user, accepted='a',
                                                 transaction__amount__lt=0)

            peers_received_from_me = IOU.objects.filter(recipient=user,
                                                        accepted='a',
                                                     transaction__amount__gt=0)

            ioupeers = {}

            for i in i_gave_to_peers:
                uid = i.recipient
                name = i.recipient.username
                amount = i.amount
                if ioupeers.has_key(uid):
                    ioupeers[uid][1] = ioupeers[uid][1] - amount
                else:
                    ioupeers[uid] = [name, -amount]

            for i in i_received_from_peers:
                uid = i.recipient
                name = i.recipient.username
                amount = i.amount
                if ioupeers.has_key(uid):
                    ioupeers[uid][1] = ioupeers[uid][1] + amount
                else:
                    ioupeers[uid] = [name, amount]

            for i in peers_gave_to_me:
                uid = i.owner
                name = i.owner.username
                amount = i.amount
                if ioupeers.has_key(uid):
                    ioupeers[uid][1] = ioupeers[uid][1] + amount
                else:
                    ioupeers[uid] = [name, amount]

            for i in peers_received_from_me:
                uid = i.owner
                name = i.owner.username
                amount = i.amount
                if ioupeers.has_key(uid):
                    ioupeers[uid][1] = ioupeers[uid][1] - amount
                else:
                    ioupeers[uid] = [name, -amount]

            ioupeerslist = []
            for peer in ioupeers.items():
                if peer[1][1] > 0:
                    ioupeerslist.append({'id':peer[0],
                                         'name':peer[1][0],
                                         'type':_('lent me'),
                                         'amount':peer[1][1]
                    })
                elif peer[1][1] < 0:
                    ioupeerslist.append({'id':peer[0],
                                         'name':peer[1][0],
                                         'type':_('owes me'),
                                         'amount':abs(peer[1][1])
                    })


            context['ioupeerslist'] = ioupeerslist
            return ''

    return IOUPeersListNode()


def do_get_ious_linked_to_recipient_transaction(parser, token):
    """
    Set the "iouslinkedtorecipienttransaction" var to the list of IOUs that
    are linked to this transaction as the recipient transaction

    Usage::

        {% getiouslinkedtorecipienttransaction %}

        <ul>
        {% for iou in iouslinkedtorecipienttransaction %}
            <li>{{ iou.owner }}</li>
        {% endfor %}
        </ul>
    """
    class IOUsLinkedToRecipientTransaction(template.Node):
        """
        List IOUs linked to a recipient transaction
        """
        def __init__(self, transaction):
            super(IOUsLinkedToRecipientTransaction, self).__init__()
            self.transaction = transaction

        def render(self, context):
            user = context['request'].user
            t = self.transaction.resolve(context)

            match = IOU.objects.filter(recipient_transaction=t,
                                    recipient_transaction__account__owner=user)
            context['iouslinkedtorecipienttransaction'] = match
            return ''

    contents = token.split_contents()
    return IOUsLinkedToRecipientTransaction(parser.compile_filter(contents[1]))


def do_get_ious_lists(parser, token):
    """
    Set the "waitingiouslist" and "rejectediouslist" vars
    to the lists of waiting and rejected ious

    Usage::

        {% getiouslists %}

        <ul>
        {% for iou in waitingiouslist %}
            <li>{{ iou.owner }}</li>
        {% endfor %}
        </ul>
        <ul>
        {% for iou in rejectediouslist %}
            <li>{{ iou.amount }}</li>
        {% endfor %}
        </ul>
    """
    class IOUsListsNode(template.Node):
        """
        List IOUs
        """
        def render(self, context):
            user = context['request'].user
            context['pendingiouslist'] = IOU.objects.filter(recipient=user,
                                                            accepted='p')
            context['rejectediouslist'] = IOU.objects.filter(
                                transaction__account__owner=user, accepted='r')
            return ''
    return IOUsListsNode()


def do_get_ious_matching_recipient_transaction(parser, token):
    """
    Set the "iousmatchingrecipienttransaction" var to the list of pending
    IOUs that could match this transaction as the recipient transaction

    Usage::

        {% getiousmatchingrecipienttransaction %}

        <ul>
        {% for iou in iousmatchingrecipienttransaction  %}
            <li>{{ iou.owner }}</li>
        {% endfor %}
        </ul>
    """
    class IOUsMatchingRecipientTransaction(template.Node):
        """
        List IOUs matching a transaction
        """

        def __init__(self, transaction):
            super(IOUsMatchingRecipientTransaction, self).__init__()
            self.transaction = transaction

        def render(self, context):
            user = context['request'].user
            t = self.transaction.resolve(context)
            origdate = t.date

            # Matching IOUs are at most 7 days later
            maxdate = origdate + datetime.timedelta(days=7)
            # Matching IOUs are at most 7 days before
            mindate = origdate - datetime.timedelta(days=7)

            if t.amount < 0:
                match = IOU.objects.filter(recipient=user,
                                           transaction__date__gte=mindate,
                                           transaction__date__lte=maxdate,
                                           transaction__amount__gt=0,
                                           amount=-t.amount,
                                           accepted='p')
            else:
                match = IOU.objects.filter(recipient=user,
                                           transaction__date__gte=mindate,
                                           transaction__date__lte=maxdate,
                                           transaction__amount__lt=0,
                                           amount=t.amount,
                                           accepted='p')

            context['iousmatchingrecipienttransaction'] = match
            return ''

    contents = token.split_contents()
    return IOUsMatchingRecipientTransaction(parser.compile_filter(contents[1]))


def do_get_notifications(parser, token):
    """
    Set the "notificationslist" var to the list of notifications

    Usage::

        {% getnotifications %}

        <ul>
        {% for n in notifications %}
            <li><a href="{{ n.link }}">{{ n.text }}</a></li>
        {% endfor %}
        </ul>
    """
    class NotificationsNode(template.Node):
        """
        Return notifications
        """
        def render(self, context):
            notifications = []
            user = context['request'].user

            # Notification for pending IOUs
            if IOU.objects.filter(recipient=user, accepted='p'):
                notifications.append({'text':_("You have pending IOU(s)!"),
                                      'link':reverse('pending_ious')})

            # Notification for rejected IOUs
            if IOU.objects.filter(owner=user, accepted='r'):
                notifications.append(
                                    {'text':_("Someone rejected your IOU(s)!"),
                                      'link':reverse('pending_ious')})

            context['notifications'] = notifications
            return ''
    return NotificationsNode()


def do_get_other_pending_ious_list(parser, token):
    """
    Set the "otherpendingiouslist" var to the lists of
    ious waiting for confirmation from other people

    Usage::

        {% getotherpendingiouslist %}

        <ul>
        {% for iou in otherpendingiouslist %}
            <li>{{ iou.amount }}</li>
        {% endfor %}
        </ul>
    """
    class OtherPendingIOUsListNode(template.Node):
        """
        List IOUs waiting for confirmation from other people
        """
        def render(self, context):
            user = context['request'].user
            context['otherpendingiouslist'] = IOU.objects.filter(
                                transaction__account__owner=user, accepted='p')
            return ''
    return OtherPendingIOUsListNode()


def do_get_transactions_matching_iou(parser, token):
    """
    Set the "transactionsmatchingiou" var to the list of transactions that
    could match an IOU

    Usage::

        {% gettransactionsmatchingiou %}

        <ul>
        {% for t in transactionsmatchingiou %}
            <li>{{ t.description }}</li>
        {% endfor %}
        </ul>
    """
    class TransactionsMatchingIOUNode(template.Node):
        """
        List transactions that could match an IOU
        """


        def __init__(self, iou):
            super(TransactionsMatchingIOUNode, self).__init__()
            self.iou = iou

        def render(self, context):
            user = context['request'].user
            iou = self.iou.resolve(context)
            origdate = iou.transaction.date

            # Positive or negative amount, depending on the IOU
            if iou.transaction.amount > 0:
                origamount = 0-iou.amount
            else:
                origamount = iou.amount

            # Matching transactions are at most 7 days later
            maxdate = origdate + datetime.timedelta(days=7)
            # Matching transactions are at most 7 days before
            mindate = origdate - datetime.timedelta(days=7)

            match = Transaction.objects.filter(account__owner=user,
                                               date__gte=mindate,
                                               date__lte=maxdate,
                                               amount=origamount)
            context['transactionsmatchingiou'] = match
            return ''
    contents = token.split_contents()
    return TransactionsMatchingIOUNode(parser.compile_filter(contents[1]))



@register.tag
def do_username(parser, token):
    """
    Display the username along with a "logout" link

    Usage::

        {% username %}
    """
    class UsernameNode(template.Node):
        """
        Username login/logout widget
        """
        def render(self, context):
            username = context['request'].user.username
            logout = reverse('logout')
            return  '%s - <a href="%s">%s</a>' % (username, logout,
                                                  _('logout'))
    return UsernameNode()


register.tag('categorytree', do_categorytree)
register.tag('contentbox', do_contentbox)
register.tag('getaccountslist', do_get_accounts_list)
register.tag('getioupeerslist', do_get_iou_peers_list)
register.tag('getiouslinkedtorecipienttransaction',
             do_get_ious_linked_to_recipient_transaction)
register.tag('getiouslists', do_get_ious_lists)
register.tag('getiousmatchingrecipienttransaction',
             do_get_ious_matching_recipient_transaction)
register.tag('getnotifications', do_get_notifications)
register.tag('getotherpendingiouslist', do_get_other_pending_ious_list)
register.tag('gettransactionsmatchingiou', do_get_transactions_matching_iou)
register.tag('username', do_username)




@register.filter
def money(amount, account):
    """
    Format the amount as a money representation,
    according to the account passed as a parameter,
    with a positive value and no sign
    """
    return mark_safe('%.2f %s' % (abs(amount), account.currency.short_name))


@register.filter
def signedmoney(amount, account):
    """
    Format the amount as a money representation,
    according to the account passed as a parameter,
    with a signed value (+ or -)

    The sign can be customized with CSS :

    * ``span.positiveamount`` for the "+" sign
    * ``span.negativeamount`` for the "-" sign
    """
    if amount > 0:
        signstr = '<span class="positiveamount">+</span>'
    else:
        signstr = '<span class="negativeamount">-</span>'
    return mark_safe('%s %.2f %s' % (signstr, abs(amount),
                                     account.currency.short_name))


register.filter(money)
register.filter(signedmoney)
