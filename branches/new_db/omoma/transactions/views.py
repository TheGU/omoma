
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from omoma.foundations.views import mainpanelview

from omoma.transactions.forms import AccountFormSet
from omoma.transactions.models import Account

@login_required
def configureaccounts(request):
    """
    Configure accounts
    """

    queryset = Account.objects.filter(owner=request.user)

    saved = False
    if request.method == 'POST':
        formset = AccountFormSet(request.POST, request.FILES, queryset=queryset)
        if formset.is_valid():
            formset.save()
            saved = True
    else:
        formset = AccountFormSet(queryset=queryset)

    return render_to_response('app/dialog/configureaccounts.html', {'formset':formset, 'saved':saved}, RequestContext(request))



# TODO delete an account...
def deleteaccount(request, accountid):
    """
    Delete an account
    """
    pass



def transactions(request):
    #~ return mainpanelview(request, 'transactions', accounts=Account.objects.filter(owner=request.user))
    return mainpanelview(request, 'transactions', submenu=True, accounts=Account.objects.filter(owner=request.user))
