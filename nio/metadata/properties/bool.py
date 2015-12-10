from nio.metadata.properties.typed import TypedProperty


class BoolProperty(TypedProperty):
    """ Defines a property for a bool type

    """

    def __init__(self, **kwargs):
        super().__init__(bool, **kwargs)

    def deserialize(self, value):
        try:
            return bool(value)
        except ValueError:
            raise ValueError("Unable to cast '{0}' to a boolean".format(value))

    def get_type_name(self):
        return bool.__name__
