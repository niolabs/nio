from weakref import WeakKeyDictionary
from nio.metadata.properties.base import Property, AllowNoneViolation


class TypedProperty(Property):
    """ Class that defines properties as descriptors by hooking into the
    attribute access mechanism, this is accomplished by overwriting the
    __get__, __set__ and __delete__ methods.

    When setting a property, the new setting type is checked to make
    sure it matches the type specified in the __init__ method.
    """

    def __init__(self, _type, title=None,
                 visible=True, allow_none=False, **kwargs):
        """ Initializes a property based on some attributes.

        Args:
            _type (class): property type (str, int, etc)

        Keyword Args:
            title (str): A display name for the property (defaults to None)
            visible (bool): Whether or not the property is visible by
                default in API calls (defaults to True)
            allow_none (bool): Whether or not this property can be None
                (defaults to False)
            kwargs: Additional attributes for the property

        Returns:
            None

        """

        self._type = _type
        if "default" in kwargs:
            self._default = kwargs["default"]
        else:
            self._default = _type()

        # handle deprecated chance
        if "deprecated" in kwargs:
            self.deprecated = kwargs["deprecated"]

        # Set up a values dictionary to keep track of values per instance
        # We want a WeakKeyDict so that instances aren't kept in memory
        # based on this property
        self._values = WeakKeyDictionary()

        # set mandatory settings if they are missing in incoming parameters
        kwargs["title"] = title
        kwargs["visible"] = visible
        kwargs["allow_none"] = allow_none
        self._kwargs = kwargs

        # make sure allow_none is consistent
        self._check_allow_none(self._default)

    # BEGIN MANDATORY DEFINITIONS (Property as Python descriptors)

    def __get__(self, instance, cls):
        return self._values.get(instance, self._default)

    def __set__(self, instance, value):

        self._check_allow_none(value)

        if value is not None and not isinstance(value, self._type):
            raise TypeError("Must be a {0}".format(self._type))
        self._values[instance] = value

    def __delete__(self, instance):
        raise AttributeError("Can't delete a property")

    # END MANDATORY DEFINITIONS

    # BEGIN Property default interface implementation

    def serialize(self, instance):
        """Return the serialized value belonging to the specified instance"""

        # TODO: Return None or default when not set
        # Returning None wouldn't "save" a value that was just set
        # by default, get would still return the default value each time
        return self._values.get(instance, self.default)

    def deserialize(self, value):
        """Return the deserialized value of the specified serialized value"""

        return value  # pragma: no cover

    def get_description(self):
        if "default" in self._kwargs:
            # make sure "default" is contained as a "serializable" version
            self._kwargs["default"] = self.default
        return dict(type=self.get_type_name(), **self._kwargs)

    def get_type_name(self):
        """ Provides a type name as a "string" for given property,
        to be overridden when default is not descriptive enough
        """
        return type(self._default).__name__

    # END Property default interface implementation

    # Helper methods
    def _check_allow_none(self, value):
        if value is None and self._kwargs["allow_none"] is False:
            raise AllowNoneViolation(
                "TypedProperty: Illegal 'None' value "
                "(expected {0})".format(self._type)
            )

    def __str__(self):
        return "type is: %s, args are %s" % (self.get_type_name(),
                                             self._kwargs)  # pragma: no cover

    @property
    def default(self):
        return self._default

    @property
    def kwargs(self):
        return self._kwargs

    @property
    def type(self):
        return self._type
