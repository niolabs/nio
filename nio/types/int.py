from nio.types.base import Type


class IntType(Type):

    @staticmethod
    def serialize(value, **kwargs):
        """ Convert a value to a JSON serializable value """
        return value

    @staticmethod
    def deserialize(value, **kwargs):
        """ Convert value to int """
        try:
            return int(value)
        except:
            raise TypeError("Unable to cast value to an int: {}".format(value))
