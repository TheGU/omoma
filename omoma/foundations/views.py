from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext

from omoma.foundations.forms import UserForm, UserProfileForm



def home(request, login=False):
    if request.user.is_authenticated():
        return redirect(request.user.get_profile().homepage)
        return ''
    else:
        return render_to_response('visitor/home.html', {'login':login}, RequestContext(request))



@login_required
def mainpanelview(request, page, **kwargs):
    pageargs = kwargs
    pageargs['menuentry'] = page
    return render_to_response('app/%s.html' % page, pageargs, RequestContext(request))



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

    return render_to_response('app/dialog/profile.html', {'userform':userform, 'profileform':profileform, 'saved':saved}, RequestContext(request))



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
