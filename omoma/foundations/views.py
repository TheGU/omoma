from django.contrib.auth.decorators import login_required
#~ from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import RequestContext

from omoma.foundations.forms import CurrencyForm, CurrencyFormSet, UserForm, UserProfileForm
from omoma.foundations.models import Currency


def home(request, login=False):
    if request.user.is_authenticated():
        return redirect(request.user.get_profile().homepage)
    else:
        return render(request, 'visitor/home.html', {'login':login})



@login_required
def mainpanelview(request, page, **kwargs):
    pageargs = kwargs
    pageargs['menuentry'] = page
    return render(request, 'app/%s.html' % page, pageargs)



@login_required
def profile(request):
    """
    User's profile
    """
    user = request.user
    profile = request.user.get_profile()

    saved = False
    if request.method == 'POST':
        userform = UserForm(request.POST, instance=user)
        if userform.is_valid():
            userform.save()
            saved = True
        profileform = UserProfileForm(request.POST, instance=profile)
        if profileform.is_valid():
            profileform.save()
            saved = True
    else:
        userform = UserForm(instance=user)
        profileform = UserProfileForm(instance=profile)

    return render(request, 'app/dialog/profile.html', {'userform':userform, 'profileform':profileform, 'saved':saved})



@login_required
def updatesidebarorder(request, order):
    profile = request.user.get_profile()
    profile.sidebarorder = order
    profile.save()
    return HttpResponse('OK', mimetype="text/plain")



@login_required
def togglesidebox(request, box):
    profile = request.user.get_profile()
    if box in profile.sidebardisplay:
        profile.sidebardisplay.remove(box)
    else:
        profile.sidebardisplay.append(box)
    profile.save()
    return HttpResponse('OK', mimetype="text/plain")



@login_required
def configurecurrencies(request, newcreated=False, deleted=False):
    """
    Configure currencies
    """

    queryset = Currency.objects.filter(owner=request.user)

    saved = False
    if request.method == 'POST' and not newcreated and not deleted:
        formset = CurrencyFormSet(request.POST, request.FILES, queryset=queryset)
        if formset.is_valid():
            formset.save()
            saved = True
    else:
        formset = CurrencyFormSet(queryset=queryset)

    return render(request, 'app/dialog/configurecurrencies.html', {'formset':formset, 'saved':saved, 'newcreated':newcreated, 'deleted':deleted})



@login_required
def newcurrency(request):
    """
    Create a new currency
    """
    if request.method == 'POST':
        form = CurrencyForm(request.POST, request.FILES)
        if form.is_valid():
            currency = form.save(commit=False)
            currency.owner = request.user
            currency.save()
            return configurecurrencies(request, newcreated=True)
    else:
        form = CurrencyForm()
    return render(request, 'app/dialog/newcurrency.html', {'form':form})



@login_required
def deletecurrency(request, currencyid):
    """
    Confirm deletion of a currency
    """
    try:
        currency = Currency.objects.get(owner=request.user, id=currencyid)
    except:
        raise PermissionDenied
    if request.method == 'POST':
        if request.POST.get('confirmdelete', None) == str(currencyid):
            currency.delete()
            return configurecurrencies(request, deleted=True)
        else:
            raise PermissionDenied
    return render(request, 'app/dialog/confirmdeletecurrency.html', {'currency':currency})
