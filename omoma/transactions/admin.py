from omoma.transactions.models import Account, Transaction, TransactionAssignment, Category, TransactionCategory, Envelope, SalaryToEnvelope, EnvelopeTransfer
from django.contrib import admin

admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(TransactionAssignment)
admin.site.register(Category)
admin.site.register(TransactionCategory)
admin.site.register(Envelope)
admin.site.register(SalaryToEnvelope)
admin.site.register(EnvelopeTransfer)
