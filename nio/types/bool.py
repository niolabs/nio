from nio.types.base import Type


class BoolType(Type):

    @staticmethod
    def serialize(value, **kwargs):
        """ Convert a value to a JSON serializable value """
        return value

    @staticmethod
    def deserialize(value, **kwargs):
        """ Convert value to bool"""
        try:
            return bool(value)
        except:
            raise TypeError("Unable to cast value to bool: {}".format(value))
