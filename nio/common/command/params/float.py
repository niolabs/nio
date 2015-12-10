"""
    NIO Float Parameter class

"""
from nio.common.command.params.typed import TypedParameter


class FloatParameter(TypedParameter):
    """ Typed parameter which expects a float value.

    """
    def __init__(self, name, title=None, default=None, allow_none=False):
        super().__init__(name, title, default, allow_none, float)

    def get_description(self):
        description = super().get_description()
        description['type'] = 'float'
        return description
