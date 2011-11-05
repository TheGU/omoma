from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
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
    if request.method == 'POST' and not newcreated and not deleted:
        formset = AccountFormSet(request.POST, request.FILES, queryset=queryset)
        if formset.is_valid():
            formset.save()
            saved = True
    else:
        formset = AccountFormSet(queryset=queryset)

    return render(request, 'app/dialog/configureaccounts.html', {'formset':formset, 'saved':saved, 'newcreated':newcreated, 'deleted':deleted})



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
    return render(request, 'app/dialog/newaccount.html', {'form':form})



@login_required
def deleteaccount(request, accountid):
    """
    Confirm deletion of an account
    """
    try:
        account = Account.objects.get(owner=request.user, id=accountid)
    except:
        raise PermissionDenied
    if request.method == 'POST':
        if request.POST.get('confirmdelete', None) == str(accountid):
            account.delete()
            return configureaccounts(request, deleted=True)
        else:
            raise PermissionDenied
    return render(request, 'app/dialog/confirmdeleteaccount.html', {'account':account})



@login_required
def transactions(request):
    return mainpanelview(request, 'transactions', submenu=True, accounts=Account.objects.filter(owner=request.user))
