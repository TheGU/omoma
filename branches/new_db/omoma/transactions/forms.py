import decimal

from django import forms
from django.db.models import Q

from gadjo.requestprovider.signals import get_request

from omoma.helpers import OmomaErrorList
from omoma.transactions.models import Account, Currency



class AmountInput(forms.widgets.TextInput):

    def __init__(self, attrs={}):
        attrs['class'] = 'amount'
        super(AmountInput, self).__init__(attrs)

    def _format_value(self, value):
        if type(value) is unicode:
            value = decimal.Decimal(value)
        return format(value, '.2f')



class AccountForm(forms.ModelForm):
    """
    Form for Accounts
    """


    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, error_class=OmomaErrorList, **kwargs)

        request = get_request()

        # Include global currencies, own currencies and currencies applied to own accounts
        # Maybe there is some bettery way than doing two requests... with only the first one, some currencies may be displayed multiple times
        currencies = Currency.objects.filter( Q(owner=request.user) | Q(owner=None) | Q(account__owner=request.user) )
        uniqcurrencies = {}
        for e in currencies:
            uniqcurrencies[e] = 1
        self.fields['currency'] = forms.ModelChoiceField(Currency.objects.filter(id__in=[currency.id for currency in uniqcurrencies.keys()]))

    class Meta:
        model = Account
        exclude = ('owner',)
        widgets = {'start_balance': AmountInput()}

AccountFormSet = forms.models.modelformset_factory(Account, AccountForm, extra=0)
