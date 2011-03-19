# Administration configuration for Omoma
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

from omoma.omoma_web.models import *
from django.contrib import admin


class TransactionCategoryInline(admin.TabularInline):
    model = TransactionCategory
    extra = 3


class IOUInline(admin.TabularInline):
    fk_name = 'transaction'
    model = IOU
    extra = 3


class BudgetInline(admin.TabularInline):
    model = Budget
    extra = 3


class CategoryAdmin(admin.ModelAdmin):
    inlines = [BudgetInline]


class TransactionAdmin(admin.ModelAdmin):
    inlines = [TransactionCategoryInline, IOUInline]


admin.site.register(Currency)
admin.site.register(Account)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Category, CategoryAdmin)
