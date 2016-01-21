from nio.metadata.properties.typed import TypedProperty, ExprFunc


class StringProperty(TypedProperty):
    """ Defines a property for a string type

    """

    def __init__(self, **kwargs):
        super().__init__(str, **kwargs)

    def deserialize(self, value):
        try:
            return str(value)
        except ValueError:
            raise ValueError("Unable to cast '{0}' to a string".format(value))

    def __get__(self, instance, cls):
        # In case we use the default, it also needs to be an ExprFunc
        default = ExprFunc(self._default, self._kwargs.get('attr_default', ''))
        return self._values.get(instance, default)

    def __set__(self, instance, value):
        self._check_allow_none(value)
        if value is not None and not isinstance(value, self._type):
            raise TypeError("Must be a {0}".format(self._type))
        # Save an ExprFunc instead of just the regular str
        self._values[instance] = ExprFunc(value, attr_default=self._kwargs.get('attr_default', ''))
