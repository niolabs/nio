import json
from nio.types.base import Type


class DictType(Type):

    @staticmethod
    def serialize(value, **kwargs):
        """ Convert a value to a JSON serializable value """
        return value

    @staticmethod
    def deserialize(value, **kwargs):
        """ Convert value to dict """
        try:
            # if a string is passed, attempt to convert it to a dict
            if isinstance(value, str):
                return json.loads(value)
            else:
                return dict(value)
        except:
            raise TypeError("Unable to cast value to a dict: {}".format(value))
