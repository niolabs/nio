from nio.types.base import Type


class FloatType(Type):

    @staticmethod
    def serialize(value, **kwargs):
        """ Convert a value to a JSON serializable value """
        return value

    @staticmethod
    def deserialize(value, **kwargs):
        """ Convert value to float """
        try:
            return float(value)
        except:
            raise TypeError("Unable to cast value to float: {}".format(value))
