# -*- coding: utf-8 -*-
# TODO Remove the header when reading db for content
from django.http import HttpResponse
from django.utils.translation import ugettext as _

from omoma.helpers import JSONResponse
from omoma.transactions.models import Account, Category



def accounts(request):
    """
    Return as JSON:
    - accounts: list of accounts with details and total:
      - name: account name
      - strbalance: balance as string
    - total: total balance as preferred
    """
    accounts = Account.objects.filter(owner=request.user)

    default_currency = request.user.get_profile().default_currency

    accountsforjson = []
    totalbalance = 0
    for account in accounts:
        totalbalance += account.balance_in_currency(default_currency)
        accountsforjson.append({
            'name': account.name,
            'strbalance': account.balance_as_string,
            'strbalancedefault': account.balance_in_currency_as_string(default_currency)
        })
    total = _('%(currency)s%(value).2f') % {'value': totalbalance, 'currency': default_currency.symbol}

    return JSONResponse(
        {
            'accounts': accountsforjson,
            'total': total
        })



def categories(request):
    """
    JSON list of categories, filtered with the "term" GET parameter
    """
    return JSONResponse([c.fullname for c in Category.objects.filter(owner=request.user, fullname__contains=request.GET.get('term', ''))])


def transactions(request):
    # TODO List transactions
    transactions = [
        {
            'id':'12',
            'description':'Pizzeria Totino',
            'original_description':'PIZZA TOTO',
            'amounts':[
                {
                    'account':'Courant',
                    'value':'CR10.00'
                },
                {
                    'account':'Espèces',
                    'value':'€4.50',
                }
            ]
        },
        {
            'id':'234',
            'description':'Restaurant japonais',
            'original_description':'',
            'amounts':[
                {
                    'account':'Top',
                    'value':'CR1.00',
                },
                {
                    'account':'Espèces',
                    'value':'€2.80',
                }
            ]
        },
        {
            'id':'532',
            'description':'tata',
            'original_description':'',
            'amounts':[
                {
                    'account':'',
                    'value':'€420.00',
                }
            ]
        },
    ]
    return JSONResponse(transactions)
