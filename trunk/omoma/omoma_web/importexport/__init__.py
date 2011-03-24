# Import/export parsers for Omoma
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

import pkgutil
import sys

from omoma_web.models import Transaction


def guessparser(filedata):
    # Iter on all modules in this directory
    for parsername in pkgutil.iter_modules(sys.modules[__name__].__path__):
        parser = __import__(parsername[1], globals())
        if 'check' in dir(parser) and parser.check(filedata):
            return parser.Parser(filedata)

    return None


def import_transaction(transaction):
    """
    Compare a transaction with existing transactions when importing,
    to import only transactions that were not imported in the past.
    Import transaction

    It compares :

     * account
     * amount
     * date
     * original description

    Return :

     * True: transaction is added
     * False: transaction already exists
     * None: error in transaction creation
    """
    account = transaction.account
    amount = transaction.amount
    date = transaction.date
    original_description = transaction.original_description

    tts = Transaction.objects.filter(date=date, amount=amount, account=account,
                                     original_description=original_description,
                                     deleted=False)
    if tts:
        return False
    else:
        try:
            transaction.save()
            return True
        except:
            return None
