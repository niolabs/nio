from weakref import WeakKeyDictionary
from nio.metadata.properties.expression.property_value import PropertyValue


class BaseProperty:
    """ Base class for metadata property definitions

    Used as a class attribute on property holders.

    Attributes:
        type (Type): The type of data held in this property.
        description (dict): Property settings.
    """

    def __init__(self, _type, title=None,
                 visible=True, allow_none=False, **kwargs):
        kwargs["title"] = title
        kwargs["visible"] = visible
        kwargs["allow_none"] = allow_none
        self.kwargs = kwargs

        self.type = _type
        self.default = kwargs.get("default", None)
        self._default_property_value = PropertyValue(
            self, self.default, validate=False)

        self._values = WeakKeyDictionary()

        self.description = dict(type=_type.data_type(), **kwargs)

    def __get__(self, instance, owner):
        """ Return the PropertyValue

        Returns:
            PropertyValue: The value for the given instance

            If a value has not been set, return a PropertyValue with the
            default value. If a value has not been set and a default is not
            defined, return None.

        Raises:
            Exception: If a value has not been set and a default is not defined
            and allow_none is False.

        """
        return self._values.get(instance, self._default_property_value)

    def __set__(self, instance, value):
        """ Save the value as a PropertyValue """
        property_value = PropertyValue(self, value)
        self._values[instance] = property_value

    def __str__(self):
        return "type is: %s, args are %s" % (self.type,
                                             self.kwargs)

    def serialize(self, instance):
        # TODO: where is serialize used? Should it really be evaluating?
        try:
            value = self.__get__(instance, instance)()
        except:
            # If property value cannot be evaluated, just get the raw value
            value = self.__get__(instance, instance).value
        return self.type.serialize(value)

    def deserialize(self, value):
        return self.type.deserialize(value)

    def get_description(self):
        return self.description
