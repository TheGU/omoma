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
Import/export parsers for Omoma
"""
# pylint: disable=E1101

import pkgutil
import sys

from omoma.omoma_web.models import Transaction, TransactionRenaming
from omoma.omoma_web.models import AutomaticCategory, TransactionCategory


def guessparser(filedata):
    """
    Guess which parser would fit to the data
    """
    # Iter on all modules in this directory
    for parsername in pkgutil.iter_modules(sys.modules[__name__].__path__):
        parser = __import__(parsername[1], globals())
        if 'check' in dir(parser) and parser.check(filedata):
            if 'instructions' in dir (parser):
                instructions = parser.instructions()
            else:
                instructions = None
            return {'parser':parser.Parser(filedata),
                    'form':parser.DetailsForm,
                    'instructions':instructions}
    return None


def listparsers():
    """
    List all parsers
    """
    parsers = []
    # List all parsers
    for parsername in pkgutil.iter_modules(sys.modules[__name__].__path__):
        parser = __import__(parsername[1], globals())
        if 'name' in dir(parser):
            parsername = parser.name()
            if parsername:
                parsers.append(parsername)
    return parsers


def import_transaction(request, transaction, duplicate=False):
    """
    Compare a transaction with existing transactions when importing,
    to import only transactions that were not imported in the past.
    Import transaction

    request: the current request

    transaction: the transaction to import

    duplicate:
     * True: create a transaction even if a similar transaction exists
     * False: do not create a transaction if a similar transaction exists

    It compares:

     * account
     * amount
     * date
     * original description

    It returns:

     * True: transaction is added
     * False: transaction already exists
     * None: error in transaction creation
    """

    if not duplicate:
        account = transaction.account
        amount = transaction.amount
        date = transaction.date
        original_description = transaction.original_description

        tts = Transaction.objects.filter(date=date, amount=amount, account=account,
                                         original_description=original_description,
                                         deleted=False)
        if tts:
            return False

    description_to_match = transaction.original_description.lower()
    renamings = TransactionRenaming.objects.filter(owner=request.user)
    for renaming in renamings:
        if renaming.original_description in description_to_match:
            transaction.description = renaming.target_description
            break
    else:
        transaction.description = transaction.original_description

    try:
        transaction.save()
    except:
        return None
