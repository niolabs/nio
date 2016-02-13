from nio.command.params.base import Parameter
from nio.types import FloatType


class FloatParameter(Parameter):

    def __init__(self, name, **kwargs):
        super().__init__(FloatType, name, **kwargs)

    def get_description(self):
        description = super().get_description()
        description['type'] = 'float'
        return description
