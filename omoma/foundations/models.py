from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext as _

from omoma.helpers import JSONDataField



class Currency(models.Model):
    """
    A currency

    - name: the currency's name
    - symbol: the currency's symbol
    - rate: the currency's rate agains the Euro
    """
    name = models.CharField(max_length=100, verbose_name=_('name'))
    symbol = models.CharField(max_length=10, verbose_name=_('short name'))
    rate = models.DecimalField(max_digits=20, decimal_places=10, default=1.00, verbose_name=_('change rate'))

    def __unicode__(self):
        """
        Full name of the currency (name and symbol)
        """
        return "%s (%s)" % (self.name, self.symbol)

    class Meta:
        verbose_name_plural = _('currencies')



class UserProfile(models.Model):
    """
    User's preferences

    - default_currency: the user's preferred currency
    - homepage: user's preferred homepage
    - sidebar: user's selected sidebar components
    """
    user = models.ForeignKey(User, unique=True)
    default_currency = models.ForeignKey(Currency, verbose_name=_('default currency'), default=1)
    homepage = models.CharField(max_length=200, verbose_name=_('home page'), default='/envelopes/')
    sidebardisplay = JSONDataField(verbose_name=_('sidebar content'), default='["sideaccounts", "sideenvelopes"]')
    sidebarorder = models.CharField(max_length=200, verbose_name=_('sidebar order'), default='sideaccounts,sideenvelopes,sidecategories,sidecommunity')

    def sidebar_as_table(self):
        return [(entry, entry in self.sidebardisplay) for entry in self.sidebarorder.split(',')]

@receiver(models.signals.post_save)
def create_profile(sender, instance, created, **kwargs):
    if sender == User:
        try:
            instance.get_profile()
        except ObjectDoesNotExist:
            profile = UserProfile(user=instance)
            profile.save()
