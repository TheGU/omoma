from django.conf.urls.defaults import include, patterns, url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.views.generic import TemplateView

from omoma.transactions.models import Account

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls), name='admin'),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {'packages': ('omoma',)}, name='jsi18n'),

    # TODO Help pages
    url(r'^help/$', TemplateView.as_view(), name='help'),
)

urlpatterns += patterns('omoma.foundations.views',

    # Visitor pages
    url(r'^$', 'home', name='home'),
    url(r'^login/$', 'home', {'login':True}, name='homelogin'),
    url(r'^logout/$', logout, {'next_page':'/'}, name='logout'),

    # Visitor dialogs
    url(r'^dialog/subscribe/$', TemplateView.as_view(template_name='visitor/dialog/subscribe.html'), name='subscribe'),
    url(r'^dialog/login/$', login, {'template_name':'visitor/dialog/login.html'}, name='login'),
    url(r'^dialog/loginok/$', TemplateView.as_view(template_name='app/dialog/successful_login.html'), name='loginok'),

    # Common user dialogs
    url(r'^dialog/profile/$', 'profile', name='profile'),

    # Sidebar manipulation
    url(r'^sidebar/updateorder/(?P<order>.+)/$',  'updatesidebarorder', name='updatesidebarorder'),
    url(r'^sidebar/toggle/(?P<box>.+)/$',  'togglesidebox', name='togglesidebox'),

    # Main pages placeholders, TODO create real views
    url(r'^envelopes/$',  'mainpanelview', {'page':'envelopes'}, name='envelopes'),
    url(r'^categories/$',  'mainpanelview', {'page':'categories'}, name='categories'),
    url(r'^community/$',  'mainpanelview', {'page':'community'}, name='community'),
)

urlpatterns += patterns('omoma.transactions.views',
    # Transactions main page
    url(r'^transactions/$',  'transactions', name='transactions'),

    # Accounts dialogs
    url(r'^dialog/accounts/$', 'configureaccounts', name='configureaccounts'),
    url(r'^dialog/newaccount/$', 'newaccount', name='newaccount'),
    url(r'^dialog/deleteaccount(?P<accountid>\d+)/$', 'confirmdeleteaccount', name='confirmdeleteaccount'),
    url(r'^dialog/deleteaccount(?P<accountid>\d+)/delete/$', 'deleteaccount', name='deleteaccount'),
)

urlpatterns += patterns('omoma.transactions.jsonviews',

    # List accounts with details
    url(r'^json/accounts/$', 'accounts', name='jsonaccounts'),

    # List categories
    url(r'^json/categories/$', 'categories', name='jsoncategories'),
    #~ url(r'^json/transactions/$', 'transactions', name='jsontransactions'),
)
