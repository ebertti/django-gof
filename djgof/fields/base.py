from django.db import models
from django.db.models import SubfieldBase
from django.utils.translation import ugettext_lazy as _


class StrategyField(models.Field):
    description = _('Strategy GOF Field')
    __metaclass__ = SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 256)
        if not 'choices' in kwargs:
            raise NotImplemented

        for item in kwargs['choices']:
            self.CLASS_DICT[item.prefix] = item()

        super(StrategyField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        return value.prefix

    def get_internal_type(self):
        return "StrategyField"

    def to_python(self, value):
        if not isinstance(value, basestring):
            return value

        if value is None or value == '':
            return None

        return self.CLASS_DICT[value]

    def get_db_prep_lookup(self, lookup_type, value, connection,
                           prepared=False):
        # We only handle 'exact' and 'in'. All others are errors.
        if lookup_type == 'exact':
            return [self.get_db_prep_save(value.prefix, connection)]
        elif lookup_type == 'in':
            return [self.get_db_prep_save(v.prefix, connection) for v in value]
        else:
            raise TypeError('Lookup type %r not supported.' % lookup_type)

    def contribute_to_class(self, cls, name):
        self.set_attributes_from_name(name)
        self.model = cls
        cls._meta.add_field(self)



