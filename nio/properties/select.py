from enum import Enum

from nio.properties import BaseProperty
from nio.types import SelectType


class SelectProperty(BaseProperty):

    def __init__(self, enum, **kwargs):
        kwargs['enum'] = enum
        super().__init__(SelectType, **kwargs)
        self.description.update(self._get_description(**kwargs))

    def _get_description(self, **kwargs):
        """ Description needs to be json serializable """
        kwargs.update(self._prepare_options(kwargs['enum']))
        kwargs.update(self._prepare_default(**kwargs))
        kwargs['enum'] = kwargs['enum'].__name__
        return kwargs

    def _prepare_options(self, enum):
        # add internal object description
        options = {}
        for val in list(enum):
            options[val.name] = val.value
        return {"options": options}

    def _prepare_default(self, **kwargs):
        """ default in description should be serializable """
        default = kwargs.get('default', None)
        if isinstance(default, Enum):
            default = default.value
        return {"default": default}
