import json

from django.http import HttpResponse
from django.utils.translation import ugettext as _

from omoma.transactions.models import Account, Category



def JSONResponse(obj):
    return HttpResponse(json.dumps(obj), mimetype="application/json")

def accounts(request):
    """
    Return as JSON:
    - accounts: list of accounts with details and total:
      - name: account name
      - strbalance: balance as string
    - total: total balance as preferred
    """
    accounts = Account.objects.filter(owner=request.user)

    totalbalance = 0
    for account in accounts:
        totalbalance += account.balance_in_default_currency()
    total = _('%(currency)s%(value).2f') % {'value': totalbalance, 'currency': request.user.get_profile().default_currency.symbol}

    return JSONResponse(
        {
            'accounts':
                [{
                    'name': a.name,
                    'strbalance': a.balance_as_string(),
                } for a in accounts],
            'total': total
        })



def categories(request):
    """
    JSON list of categories, filtered with the "term" GET parameter
    """
    return JSONResponse([c.fullname for c in Category.objects.filter(owner=request.user, fullname__contains=request.GET.get('term', ''))])


def transactions(request):
    # TODO List transactions
    return HttpResponse('')
