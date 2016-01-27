from nio.metadata.types.base import Type


class StringType(Type):

    @staticmethod
    def data_type():
        return "str"

    @staticmethod
    def serialize(value):
        """ Convert a value to a JSON serializable value """
        return value

    @staticmethod
    def deserialize(value):
        """ Convert value to string """
        try:
            return str(value)
        except:
            raise TypeError("Unable to cast value to a string")
