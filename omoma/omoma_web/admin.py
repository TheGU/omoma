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
Administration configuration for Omoma
"""
# pylint: disable=R0904

from omoma.omoma_web.models import Account, Budget, Category, Currency, IOU
from omoma.omoma_web.models import Transaction, TransactionCategory
from omoma.omoma_web.models import AutomaticCategory, TransactionRenaming
from django.contrib import admin


class TransactionCategoryInline(admin.TabularInline):
    """
    Administration stuff...
    """
    model = TransactionCategory
    extra = 3


class IOUInline(admin.TabularInline):
    """
    Administration stuff...
    """
    fk_name = 'transaction'
    model = IOU
    extra = 3


class BudgetInline(admin.TabularInline):
    """
    Administration stuff...
    """
    model = Budget
    extra = 3


class CategoryAdmin(admin.ModelAdmin):
    """
    Administration stuff...
    """
    inlines = [BudgetInline]


class TransactionAdmin(admin.ModelAdmin):
    """
    Administration stuff...
    """
    inlines = [TransactionCategoryInline, IOUInline]


admin.site.register(Currency)
admin.site.register(Account)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(AutomaticCategory)
admin.site.register(TransactionRenaming)
