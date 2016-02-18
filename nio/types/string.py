from nio.types.base import Type


class StringType(Type):

    @staticmethod
    def serialize(value, **kwargs):
        """ Convert a value to a JSON serializable value """
        return value

    @staticmethod
    def deserialize(value, **kwargs):
        """ Convert value to string """
        if value is None:
            # It doesn't make sense for None to deserialize to "None"
            return None
        try:
            return str(value)
        except:
            raise TypeError("Unable to cast value to a string")
