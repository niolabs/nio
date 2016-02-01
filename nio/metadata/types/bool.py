from nio.metadata.types.base import Type


class BoolType(Type):

    @staticmethod
    def data_type():
        return "bool"

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
