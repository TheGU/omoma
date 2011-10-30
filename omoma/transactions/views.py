
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from omoma.foundations.views import mainpanelview

from omoma.transactions.forms import AccountForm, AccountFormSet
from omoma.transactions.models import Account

@login_required
def configureaccounts(request, newcreated=False, deleted=False):
    """
    Configure accounts
    """

    queryset = Account.objects.filter(owner=request.user)

    saved = False
    if request.method == 'POST' and not newcreated:
        formset = AccountFormSet(request.POST, request.FILES, queryset=queryset)
        if formset.is_valid():
            formset.save()
            saved = True
    else:
        formset = AccountFormSet(queryset=queryset)

    return render_to_response('app/dialog/configureaccounts.html', {'formset':formset, 'saved':saved, 'newcreated':newcreated, 'deleted':deleted}, RequestContext(request))



@login_required
def newaccount(request):
    """
    Create a new account
    """

    if request.method == 'POST':
        form = AccountForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            form.instance.owner.add(request.user)
            form.save()
            return configureaccounts(request, newcreated=True)
    else:
        form = AccountForm()
    return render_to_response('app/dialog/newaccount.html', {'form':form}, RequestContext(request))



@login_required
def confirmdeleteaccount(request, accountid):
    """
    Confirm deletion of an account
    """
    try:
        account = Account.objects.get(owner=request.user, id=accountid)
    except:
        # TODO Raise an exception or do something else because the account is not found (not authorized or something like that)
        pass
    return render_to_response('app/dialog/confirmdeleteaccount.html', {'account':account}, RequestContext(request))



@login_required
def deleteaccount(request, accountid):
    """
    Delete an account
    """
    try:
        account = Account.objects.get(owner=request.user, id=accountid)
    except:
        # TODO Raise an exception or do something else because the account is not found (not authorized or something like that)
        pass
    account.delete()
    return configureaccounts(request, deleted=True)



@login_required
def transactions(request):
    return mainpanelview(request, 'transactions', submenu=True, accounts=Account.objects.filter(owner=request.user))
