# Copyright 2011 Alin Voinea
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
""" Custom auth forms
"""

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

class UserForm(forms.ModelForm):
    """ User form
    """
    new_password = forms.CharField(widget=forms.PasswordInput,
                                   label=_("Password"), required=False)
    confirm = forms.CharField(widget=forms.PasswordInput,
                              label=_("Password (again)"), required=False)

    def __init__(self, *args, **kwargs):
        super (UserForm, self).__init__(*args, **kwargs)

    # pylint: disable=C0111,W0232,R0903
    class Meta:
        model = User
        exclude = ('is_staff', 'is_active', 'is_superuser',
                   'last_login', 'date_joined',
                   'groups', 'user_permissions', 'password')

    def clean_confirm(self):
        """ Validate and clean confirm field
        """
        confirm = self.cleaned_data['confirm']
        if self.cleaned_data['new_password'] != confirm:
            raise forms.ValidationError(
                _("The two password fields didn't match."))
        return confirm

    def save(self, commit=True):
        """ Save form
        """
        password = self.cleaned_data['new_password']
        if password:
            self.instance.set_password(password)
        super(UserForm, self).save()
