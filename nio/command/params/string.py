"""
    NIO String Parameter class

"""
from nio.command.params.typed import TypedParameter


class StringParameter(TypedParameter):
    """ A command parameter expecting a string

    """
    def __init__(self, name, title=None, default=None, allow_none=False):
        super().__init__(name, title, default, allow_none, str)

    def get_description(self):
        description = super().get_description()
        description['type'] = 'string'
        return description
