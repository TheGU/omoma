# Django URLs for Omoma
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

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic.create_update import delete_object
from django.views.generic.simple import direct_to_template

admin.autodiscover()

urlpatterns = patterns('django.contrib.auth.views',
    # Login and logout...
    (r'^login/', 'login', {'template_name':'login.html'}, 'login'),
    (r'^logout/', 'logout_then_login', None, 'logout'),
)

urlpatterns += patterns('',
    # Common stuff... files, admin...
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
                                       {'document_root': settings.STATIC_ROOT}),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('omoma.omoma_web.views_account',
    # Accounts list
    (r'^account/$', 'accounts', None, 'accounts'),
    # Single account view
    (r'^account/(?P<aid>\d+)/edit/$', 'account', None, 'account'),
    # New account
    (r'^account/new/$', 'account', None, 'new_account'),
    # Delete account
    (r'^account/(?P<aid>\d+)/delete/$', 'delete_account', None, 'delete_account'),
)

urlpatterns += patterns('omoma.omoma_web.views_cleaning',
    # Cleaning home
    (r'^cleaning/$', direct_to_template, {'template': 'cleaning.html'}, 'cleaning'),
)

urlpatterns += patterns('omoma.omoma_web.views_transaction',
    # Transactions list
    (r'^$', 'transactions', None, 'transactions'),
    (r'^account/(?P<aid>\d+)/$', 'transactions', None, 'transactions'),
    (r'^deleted/$', 'transactions', {'deleted':True}, 'deleted_transactions'),
    # Single transaction view
    (r'^(?P<tid>\d+)/$', 'transaction', None, 'transaction'),
    (r'^account/(?P<aid>\d+)/(?P<tid>\d+)/$', 'transaction', None, 'transaction'),
    # New transaction
    (r'^new/$', 'transaction', None, 'new_transaction'),
    (r'^account/(?P<aid>\d+)/new/$', 'transaction', None, 'new_transaction'),
    (r'^iou/(?P<iid>\d+)/new/$', 'transaction', None, 'new_transaction'),
    # Remove deleted transactions
    (r'^deleted/remove/$', 'remove_deleted_transactions', None, 'remove_deleted_transactions'),
    # Validate transaction
    (r'^(?P<tid>\d+)/validate/$', 'validate_transaction', None, 'validate_transaction'),
    (r'^account/(?P<aid>\d+)/(?P<tid>\d+)/validate/$', 'validate_transaction', None, 'validate_transaction'),
    # Restore transaction
    (r'^deleted/(?P<tid>\d+)/$', 'delete_transaction', {'restore':True}, 'restore_transaction'),
    # Delete transaction
    (r'^(?P<tid>\d+)/delete/$', 'delete_transaction', None, 'delete_transaction'),
    (r'^account/(?P<aid>\d+)/(?P<tid>\d+)/delete/$', 'delete_transaction', None, 'delete_transaction'),
)

urlpatterns += patterns('omoma.omoma_web.views_transactioncategory',
    # New transactioncategory
    (r'^(?P<tid>\d+)/new/$', 'transactioncategory', None, 'new_transactioncategory'),
    (r'^account/(?P<aid>\d+)/(?P<tid>\d+)/new/$', 'transactioncategory', None, 'new_transactioncategory'),
    # Single transactioncategory view
    (r'^(?P<tid>\d+)/(?P<cid>\d+)/$', 'transactioncategory', None, 'transactioncategory'),
    (r'^account/(?P<aid>\d+)/(?P<tid>\d+)/(?P<cid>\d+)/$', 'transactioncategory', None, 'transactioncategory'),
    # Delete transactioncategory
    (r'^(?P<tid>\d+)/(?P<cid>\d+)/delete/$', 'delete_transactioncategory', None, 'delete_transactioncategory'),
    (r'^account/(?P<aid>\d+)/(?P<tid>\d+)/(?P<cid>\d+)/delete/$', 'delete_transactioncategory', None, 'delete_transactioncategory'),
)

urlpatterns += patterns('omoma.omoma_web.views_iou',
    # IOUs lists
    (r'^iou/$', 'ious', None, 'ious'),
    (r'^iou/(?P<recipient>\w+)/$', 'ious', None, 'ious'),
    (r'^pending/$', direct_to_template, {'template': 'pending_ious.html'}, 'pending_ious'),
    # Single IOU view
    (r'^iou/(?P<iid>\d+)/$', 'iou', None, 'iou'),
    (r'^iou/(?P<iid>\d+)/(?P<tid>\d+)/$', 'iou', None, 'iou'),
    (r'^iou-(?P<iid>\d+)/(?P<tid>\d+)/(?P<aid>\d+)/$', 'iou', None, 'iou'),
    (r'^pending/(?P<iid>\d+)/$', 'iou', {'rejected':True}, 'rejected_iou'),
    # New IOU
    (r'^iou/new/(?P<tid>\d+)/$', 'iou', None, 'new_iou'),
    (r'^iou/new/(?P<tid>\d+)/(?P<aid>\d+)/$', 'iou', None, 'new_iou'),
    # Delete IOU
    (r'^iou/(?P<iid>\d+)/delete/$', 'delete_iou', None, 'delete_iou'),
    (r'^iou/(?P<iid>\d+)/(?P<tid>\d+)/delete/$', 'delete_iou', None, 'delete_iou'),
    (r'^iou/(?P<iid>\d+)/(?P<tid>\d+)/(?P<aid>\d+)/delete/$', 'delete_iou', None, 'delete_iou'),
    (r'^pending/(?P<iid>\d+)/delete/$', 'delete_iou', {'rejected':True}, 'delete_rejected_iou'),
    # Attach IOU
    (r'^pending/(?P<iid>\d+)/attach/$', 'attach_iou', None, 'attach_iou'),
    (r'^iou/(?P<iid>\d+)/(?P<tid>\d+)/attach/$', 'attach_iou_to_transaction', None, 'attach_iou_to_transaction'),
    (r'^iou/(?P<iid>\d+)/(?P<tid>\d+)/(?P<aid>\d+)/attach/$', 'attach_iou_to_transaction', None, 'attach_iou_to_transaction'),
    (r'^pending/(?P<iid>\d+)/(?P<tid>\d+)/attach/$', 'attach_iou_to_transaction', {'from_ious':True}, 'attach_transaction_to_iou'),
    # Detach IOU
    (r'^iou/(?P<iid>\d+)/(?P<tid>\d+)/detach/$', 'detach_iou_from_transaction', None, 'detach_iou_from_transaction'),
    (r'^iou/(?P<iid>\d+)/(?P<tid>\d+)/(?P<aid>\d+)/detach/$', 'detach_iou_from_transaction', None, 'detach_iou_from_transaction'),
    # Accept IOU
    (r'^pending/(?P<iid>\d+)/accept/$', 'accept_iou', None, 'accept_iou'),
    (r'^pending/accept/$', 'accept_all_ious', None, 'accept_all_ious'),
    # Reject IOU
    (r'^iou/(?P<iid>\d+)/reject/$', 'reject_iou', None, 'reject_iou'),
    (r'^pending/(?P<iid>\d+)/reject/$', 'reject_iou', {'pending':True}, 'reject_pending_iou'),
)

urlpatterns += patterns('omoma.omoma_web.views_category',
    # Categories list
    (r'^category/$', 'categories', None, 'categories'),
    # New category
    (r'^category/new/$', 'category', None, 'new_category'),
    # Single category view
    (r'^category/(?P<cid>\d+)/$', 'category', None, 'category'),
    # Delete category
    (r'^category/(?P<cid>\d+)/delete/$', 'delete_category', None, 'delete_category'),
)

urlpatterns += patterns('omoma.omoma_web.views_import',
    # Choose import format
    (r'^import/$', 'import_transactions', None, 'import_transactions'),
    (r'^account/(?P<aid>\d+)/import/$', 'import_transactions', None, 'import_transactions'),
    # Cancel import
    (r'^import/cancel/$', 'cancel_import_transactions', None, 'cancel_import_transactions'),
    (r'^account/(?P<aid>\d+)/import/cancel/$', 'cancel_import_transactions', None, 'cancel_import_transactions'),
)
