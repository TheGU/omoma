from django.db import models
from django.forms.util import ErrorList
from django.utils import simplejson

class OmomaErrorList(ErrorList):

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
