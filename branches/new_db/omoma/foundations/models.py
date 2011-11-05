from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, router
from django.db.models import Q
from django.dispatch import receiver
from django.utils.translation import ugettext as _

from omoma.helpers import JSONDataField



class Currency(models.Model):
    """
    A currency

    - owner: the currency's owner (if it's not a global currency)
    - name: the currency's name
    - symbol: the currency's symbol
    - rate: the currency's rate agains the Euro
    """
    owner = models.ForeignKey(User, null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name=_('name'))
    symbol = models.CharField(max_length=10, verbose_name=_('symbol'))
    rate = models.DecimalField(max_digits=20, decimal_places=10, default=1.00, verbose_name=_('exchange rate'))

    def __unicode__(self):
        """
        Full name of the currency (name and symbol)
        """
        return "%s (%s)" % (self.name, self.symbol)

    def rate_to_currency(self, currency):
        """
        Rate from this currency to the specified currency
        """
        return self.rate / currency.rate


    def rate_to_currency_as_string(self, currency):
        """
        Rate from this currency to the specified currency as a string
        """
        rate = self.rate_to_currency(currency)
        return _(u'%(symbol)s1=%(comparedsymbol)s%(rate).2f') % {'symbol':self.symbol, 'comparedsymbol':currency.symbol, 'rate':rate}

    def is_used(self):
        """
        Return True if the currency is in use or False if it is not used (and can be deleted)
        """
        using = router.db_for_write(self.__class__, instance=self)
        collector = models.deletion.Collector(using=using)
        collector.collect([self])
        if len(collector.data.keys()) <= 1:
            return False
        return True

    class Meta:
        verbose_name_plural = _('currencies')


def user_currencies(user):
    """
    Return currencies available for a single user :
    - global currencies
    - his own currencies
    - currencies applied on his accounts
    """
    # Maybe there is some bettery way than doing two requests... with only the first one, some currencies may be displayed multiple times
    currencies = Currency.objects.filter( Q(owner=user) | Q(owner=None) | Q(account__owner=user) )
    uniqcurrencies = {}
    for e in currencies:
        uniqcurrencies[e] = 1
    return Currency.objects.filter(id__in=[currency.id for currency in uniqcurrencies.keys()])



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
    sidebardisplay = JSONDataField(verbose_name=_('displayed sidebar content'), default='["sideaccounts", "sideenvelopes"]')
    sidebarorder = models.CharField(max_length=200, verbose_name=_('sidebar order'), default='sideaccounts,sideenvelopes,sidecategories,sidecommunity,sidecurrencies')

    def __unicode__(self):
        """
        Full name of the currency (name and symbol)
        """
        return str(self.user)

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
