from nio.command.params.base import Parameter
from nio.types import StringType


class StringParameter(Parameter):

    def __init__(self, name, **kwargs):
        super().__init__(StringType, name, **kwargs)
