from nio.metadata.properties.typed import TypedProperty


class VarProperty(TypedProperty):
    def __init__(self, _type=object, **kwargs):
        """ Initializes a var property.

        Keyword Args:
            Property definitions

        """
        super().__init__(_type, **kwargs)

    def get_type_name(self):
        return "var"
