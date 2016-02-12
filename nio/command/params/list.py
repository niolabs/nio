"""
    NIO List Parameter class

"""
from nio.command.params.typed import TypedParameter


class ListParameter(TypedParameter):
    """ A command parameter expecting a list

    """
    def __init__(self, name, title=None, default=[], allow_none=False):
        super().__init__(name, title, default, allow_none, lambda x: x)

    def get_description(self):
        description = super().get_description()
        description['type'] = 'list'
        return description
