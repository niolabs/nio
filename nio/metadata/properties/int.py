from nio.metadata.properties.typed import TypedProperty


class IntProperty(TypedProperty):

    """ Defines a property for an integer type

    """

    def __init__(self, **kwargs):
        super().__init__(int, **kwargs)

    def deserialize(self, value):
        try:
            return int(value)
        except ValueError:
            raise ValueError("Unable to cast '{}' to an integer".format(value))

    def get_type_name(self):
        return int.__name__
