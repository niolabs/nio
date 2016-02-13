from nio.command.params.base import Parameter
from nio.types import DictType


class DictParameter(Parameter):

    def __init__(self, name, **kwargs):
        super().__init__(DictType, name, **kwargs)

    def get_description(self):
        description = super().get_description()
        description['type'] = 'dict'
        return description
