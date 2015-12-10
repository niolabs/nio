from nio.metadata.properties.typed import TypedProperty
from nio.metadata.properties.holder import PropertyHolder


class ObjectProperty(TypedProperty):
    """ Defines a property for an object type.
    Object types contain properties themselves, and must inherit from
    PropertyHolder just like the parent class.

    """

    def __init__(self, obj_type, **kwargs):
        """ Initializes the property.

        Args:
            obj_type (class): class type which is an instance of PropertyHolder

        Keyword Args:
            Property definitions

        Raises:
            TypeError: if the object type is not a PropertyHolder

        """
        # Validate that the object is a PropertyHolder
        if not issubclass(obj_type, PropertyHolder):
            raise TypeError("Specified object type %s is not a PropertyHolder"
                            % obj_type.__class__)

        super().__init__(obj_type, **kwargs)

    def serialize(self, instance):
        value = self.__get__(instance, self.__class__)
        if value is not None:
            return value.to_dict()

    def deserialize(self, value):
        sub_instance = self._type()
        sub_instance.from_dict(value)
        return sub_instance

    def get_description(self):
        description = super().get_description()
        # add internal object description
        description.update({"template": self._type().get_description()})
        return description

    @property
    def default(self):
        if isinstance(self._default, PropertyHolder):
            return self._default.get_defaults()
        else:
            return super().default

    def get_type_name(self):
        """ Specifies the type name to return.

        We want to return a type name of "object" rather than the individual
        type's class name.
        """
        return "object"
