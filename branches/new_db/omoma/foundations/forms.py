from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from omoma.foundations.models import UserProfile

from omoma.helpers import OmomaErrorList

class UserForm(forms.ModelForm):
    """ User form
    """
    new_password = forms.CharField(widget=forms.PasswordInput, label=_("Password"), required=False)
    confirm = forms.CharField(widget=forms.PasswordInput, label=_("Password (again)"), required=False)

    def __init__(self, *args, **kwargs):
        super (UserForm, self).__init__(*args, error_class=OmomaErrorList, **kwargs)

    class Meta:
        model = User
        exclude = ('username', 'is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined', 'groups', 'user_permissions', 'password')

    def clean_confirm(self):
        """ Validate and clean confirm field
        """
        confirm = self.cleaned_data['confirm']
        if self.cleaned_data['new_password'] != confirm:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return confirm

    def save(self, commit=True):
        """ Save form
        """
        password = self.cleaned_data['new_password']
        if password:
            self.instance.set_password(password)
        super(UserForm, self).save()


class UserProfileForm(forms.ModelForm):
    """
    Form for UserProfile
    """

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, error_class=OmomaErrorList, **kwargs)

        choices = [
            ('/transactions/', _('All transactions')),
            ('/envelopes/', _('All envelopes')),
            ('/categories/', _('All categories')),
        ]
        self.fields['homepage'] = forms.ChoiceField(choices)


    class Meta:
        model = UserProfile
        exclude = ('user', 'sidebar')
