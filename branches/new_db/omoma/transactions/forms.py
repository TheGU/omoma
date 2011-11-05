import decimal

from django import forms

from gadjo.requestprovider.signals import get_request

from omoma.helpers import AmountInput, OmomaErrorList
from omoma.foundations.models import user_currencies
from omoma.transactions.models import Account



class AccountForm(forms.ModelForm):
    """
    Form for Accounts
    """

    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, error_class=OmomaErrorList, **kwargs)
        self.fields['currency'] = forms.ModelChoiceField(user_currencies(get_request().user))

    class Meta:
        model = Account
        exclude = ('owner',)
        widgets = {'start_balance': AmountInput()}

AccountFormSet = forms.models.modelformset_factory(Account, AccountForm, extra=0)
