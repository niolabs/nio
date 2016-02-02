from weakref import WeakKeyDictionary
from nio.metadata.properties.expression.property_value import PropertyValue


class BaseProperty:
    """ Base class for metadata property definitions

    Used as a class attribute on property holders.

    Attributes:
        type (Type): The type of data held in this property.
        description (dict): Property settings.
    """

    def __init__(self, _type=object, title=None,
                 visible=True, allow_none=False, **kwargs):
        kwargs["title"] = title
        kwargs["visible"] = visible
        kwargs["allow_none"] = allow_none
        self.kwargs = kwargs

        self.type = _type
        if "default" in kwargs:
            # Store default as the deserialized version
            # TODO: comment this better. why deserialize this?
            self.default = \
                self.deserialize(kwargs.get("default", None), **kwargs)
        else:
            self.default = None
        self._default_property_value = PropertyValue(
            self, kwargs.get("default", None), validate=False)

        self._values = WeakKeyDictionary()

        try:
            self.description = dict(type=_type.data_type(), **kwargs)
        except:
            # Some types have not defined a data_type
            self.description = dict(type=str(_type), **kwargs)

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
        value = self._values.get(instance, None)
        return self._values.get(instance, self._default_property_value)

    def __set__(self, instance, value):
        """ Save the value as a PropertyValue """
        property_value = PropertyValue(self, value)
        self._values[instance] = property_value

    def __str__(self):
        return "type is: %s, args are %s" % (self.type,
                                             self.kwargs)

    def serialize(self, instance, **kwargs):
        """ Serialze and return the value of an instance of this property

        Serialize is defined by the Type associated with this Property.

        Args:
            instance (PropertyHolder): PropertyHolder that the property is on
        Keyword Args:
            Optionally override the kwargs of the property
            TODO: give an example of when this is useful
        Returns:
            Serialized version of property value

        """
        # Allow property kwargs to be overriden by call to serialize
        merged_kwargs = self.kwargs.copy()
        merged_kwargs.update(**kwargs)
        # Use the default value if the specified instance does not have a value
        value = self.__get__(instance, instance).value or \
            merged_kwargs["default"]
        # TODO: for non-string properties, this can return a string if it's an
        # expression
        return self.type.serialize(value, **merged_kwargs)

    def deserialize(self, value, **kwargs):
        """ Deserialize a value of this property

        Deserialize is defined by the Type associated with this Property.

        Args:
            value: value to be deserialized. Various data formats are accepted
                based on the property Type.
        Keyword Args:
            Optionally override the kwargs of the property
            TODO: give an example of when this is useful
        Returns:
            Deserialized version of property value

        """
        if not self.is_expression(value) and not self.is_env_var(value):
            # Allow property kwargs to be overriden by call to serialize
            merged_kwargs = self.kwargs.copy()
            merged_kwargs.update(**kwargs)
            return self.type.deserialize(value, **merged_kwargs)
        # TODO: else raise exception?
        return value

    def get_description(self):
        return self.description

    def is_expression(self, value):
        # TODO: this code should not be both here and in evaluator
        try:
            return "{{" in value and \
                    "}}" in value
        except:
            return False

    def is_env_var(self, value):
        try:
            return value.startswith("[[") and \
                    value.endswith("]]")
        except:
            return False
