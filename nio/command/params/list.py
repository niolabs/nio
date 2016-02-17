from nio.command.params.base import Parameter
from nio.types import ListType


class ListParameter(Parameter):

    def __init__(self, list_obj_type, name, **kwargs):
        kwargs['list_obj_type'] = list_obj_type
        super().__init__(ListType, name, **kwargs)
