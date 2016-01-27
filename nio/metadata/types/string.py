from nio.metadata.types.base import Type


class StringType(Type):

    def __init__(self):
        super().__init__()
        self.default = str()

    @classmethod
    def serialize(cls, value):
        """ Convert a value to a JSON serializable value """
        return value

    @classmethod
    def deserialize(cls, value):
        """ Convert value to string """
        try:
            return str(value)
        except:
            raise TypeError("Unable to cast value to a string")
