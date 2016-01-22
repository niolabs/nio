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
