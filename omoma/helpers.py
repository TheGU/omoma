import json

from django import forms
from django.db import models
from django.http import HttpResponse
from django.utils import simplejson



class AmountInput(forms.widgets.TextInput):

    def __init__(self, attrs={}):
        attrs['class'] = 'amount'
        super(AmountInput, self).__init__(attrs)

    def _format_value(self, value):
        if type(value) is unicode:
            value = decimal.Decimal(value)
        return format(value, '.2f')



class OmomaErrorList(forms.util.ErrorList):

    def __unicode__(self):
        return self.as_divs()

    def as_divs(self):
        if not self: return u''
        return u'<div class="ui-widget">%s</div>' % ''.join([u'<div class="ui-state-error ui-corner-all" style="padding: 0 .7em;">%s</div>' % e for e in self])



class JSONDataField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if value is None:
            return None
        if not isinstance(value, basestring):
            return value
        return simplejson.loads(value)

    def get_db_prep_save(self, value):
        if value is None:
            return None
        return simplejson.dumps(value)

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^omoma\.helpers\.JSONDataField"])

def JSONResponse(obj):
    return HttpResponse(json.dumps(obj), mimetype="application/json")
