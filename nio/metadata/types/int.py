from nio.metadata.types.base import Type


class IntType(Type):

    @staticmethod
    def data_type():
        return "int"

    @staticmethod
    def serialize(value):
        """ Convert a value to a JSON serializable value """
        return value

    @staticmethod
    def deserialize(value):
        """ Convert value to int """
        try:
            return int(value)
        except:
            raise TypeError("Unable to cast value to an int: {}".format(value))
