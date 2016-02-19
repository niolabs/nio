from weakref import WeakKeyDictionary

from nio.properties.util.property_value import PropertyValue


class BaseProperty(object):
    """ Base class for metadata property definitions

    Used as a class attribute on property holders.

    Attributes:
        type (Type): The type of data held in this property.
        description (dict): Property settings.
    """

    def __init__(self, _type, title=None,
                 visible=True, allow_none=False, default=None, **kwargs):
        self.type = _type
        self.title = title
        self.visible = visible
        self.allow_none = allow_none
        self.kwargs = kwargs

        # Default value info
        self._default = default
        self._cached_default = None
        self._default_property_value = PropertyValue(self, self._default)

        # Set up a values dictionary to keep track of values per instance
        # We want a WeakKeyDict so that instances aren't kept in memory
        # based on this property
        self._values = WeakKeyDictionary()

        # Description needs to be serializble so save type as __name__
        self.description = dict(type=_type.__name__,
                                title=title,
                                visible=visible,
                                allow_none=allow_none,
                                default=default,
                                **kwargs)

    @property
    def default(self):
        """ default deserialized value, not a callable PropertyValue """
        if self._cached_default is None and self._default is not None:
            self._cached_default = \
                self.deserialize(self._default, **self.kwargs)
        return self._cached_default

    def __get__(self, instance, owner):
        """ Return the PropertyValue

        Overriding __set__ and __get__ so values can be saved and retrieved
        as callable PropertyValues instead of the raw value.

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
        """ Save the value as a PropertyValue

        Overriding __set__ and __get__ so values can be saved and retrieved
        as callable PropertyValues instead of the raw value.

        """
        self._values[instance] = PropertyValue(self, value)

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
        property_value = self.__get__(instance, instance.__class__)
        # Get the raw value from the PropertyValue
        value = property_value.value
        if value is not None and \
                not self.is_expression(value) and not self.is_env_var(value):
            return self.type.serialize(value, **merged_kwargs)
        else:
            # If the value is None or if it's an expression property,
            # then don't try to serialize it
            return value

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
        return value

    def is_expression(self, value):
        """ A property value is an expression if contatins expression syntax

        An expression is identified by a pair of opening curly braces and then
        later a pair of closing curly braces.

        Returns:
            bool: True if value is an expression

        Examples:
            >>> is_expression("{{ 1 + 2 }}")
            True
            >>> is_expression("1 + 2")
            False
            >>> is_expression("{{ 1 + 2")
            False
            >>> is_expression("{ { 1 + 2 } }")
            False

        """

        try:
            # TODO: This check should actually check if the closing braces come
            # after the opening ones.
            return "{{" in value and \
                    "}}" in value
        except:
            return False

    def is_env_var(self, value):
        """ Determine if property value is an environment variable

        Environment variables are identified by a pair of opening square braces
        that are eventually followed by a pair of closing square braces.

        It is significant to differently identify a value *containing* an env
        var and a value that *is* an env var. If a value *is* an env var then
        it is valid for that value to be string even if the proprety type can
        not normally be represented as a string.

        Returns:
            bool: True if value is an environment variable

        Examples:
            >>> is_env_var("[[ENV_VAR]]")
            True
            >>> is_env_var("No an [[ENV_VAR]]")
            False

        """

        try:
            return value.startswith("[[") and \
                    value.endswith("]]")
        except:
            return False
