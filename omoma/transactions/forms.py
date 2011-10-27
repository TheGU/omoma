import decimal

from django import forms

from omoma.transactions.models import Account



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

    class Meta:
        model = Account
        exclude = ('owner',)
        widgets = {'start_balance': AmountInput()}

AccountFormSet = forms.models.modelformset_factory(Account, AccountForm, extra=0)
