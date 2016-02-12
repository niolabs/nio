"""
    NIO Integer Parameter class

"""
from nio.command.params.typed import TypedParameter


class IntParameter(TypedParameter):
    """ Typed parameter which expects an integer value.

    """
    def __init__(self, name, title=None, default=None, allow_none=False):
        super().__init__(name, title, default, allow_none, int)

    def get_description(self):
        description = super().get_description()
        description['type'] = 'int'
        return description
