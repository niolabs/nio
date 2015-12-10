from nio.metadata.properties.typed import TypedProperty


class FloatProperty(TypedProperty):
    """ Defines a property for a float type

    """

    def __init__(self, **kwargs):
        super().__init__(float, **kwargs)

    def deserialize(self, value):
        try:
            return float(value)
        except ValueError:
            raise ValueError("Unable to cast '{0}' to a float".format(value))

    def get_type_name(self):
        return float.__name__
