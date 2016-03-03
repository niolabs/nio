from enum import Enum
from nio.types.base import Type


class SelectType(Type):

    @staticmethod
    def serialize(value, **kwargs):
        """ Convert a value to a JSON serializable value """
        if value is not None and isinstance(value, Enum):
            return value.name
        return str(value)

    @staticmethod
    def deserialize(value, **kwargs):
        """ Convert value to select

        Keyword Args:
            enum (Enum): Enumeration type
        """
        # Value can be an Enum
        if isinstance(value, Enum):
            return value

        # Value can be a string equal the name or value of the Enum
        for name, member in kwargs.get('enum').__members__.items():
            if name == value or member.value == value:
                return member

        raise TypeError("{} does not match enum type: {}".format(
            value, kwargs.get('enum')))
