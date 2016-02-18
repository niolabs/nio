from nio.command.params.base import Parameter
from nio.types import IntType


class IntParameter(Parameter):

    def __init__(self, name, **kwargs):
        super().__init__(IntType, name, **kwargs)
