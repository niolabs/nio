from enum import Enum
from nio.metadata.properties.typed import TypedProperty


class SelectProperty(TypedProperty):

    """ Defines a property for an object type.
    Object types contain properties themselves, and must inherit from
    PropertyHolder just like the parent class.

    """

    def __init__(self, enum_type, **kwargs):
        """ Initializes the property.

        Args:
            name (str): property name
            options (dict): select options

        Keyword Args:
            Property definitions

        """

        # Looking for a default, try using index 1
        default = kwargs.get("default")
        if not default:
            kwargs['default'] = enum_type(0)

        super().__init__(Enum, **kwargs)
        self.enum_type = enum_type

    def serialize(self, instance):
        value = self.__get__(instance, self.__class__)
        if value is not None and isinstance(value, Enum):
            return value.name

        return str(value)

    def deserialize(self, value):
        if isinstance(value, Enum):
            return value

        for name, member in self.enum_type.__members__.items():
            if name == value or member.value == value:
                return member

        raise TypeError(
            "{0} does not match enum type: {1}".format(value, self.enum_type))

    def get_description(self):
        description = super().get_description()
        default = description['default']
        if isinstance(default, Enum):
            description['default'] = default.value
        # add internal object description
        descr = {}
        for val in list(self.enum_type):
            descr[val.name] = val.value
        description.update({"options": descr})
        return description

    def get_type_name(self):
        return "select"

    @property
    def default(self):
        return self._default
