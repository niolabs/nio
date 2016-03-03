from datetime import timedelta
from nio.types import Type


class TimeDeltaType(Type):

    @staticmethod
    def serialize(value, **kwargs):
        """ Convert a value to a JSON serializable value """
        if isinstance(value, timedelta) or isinstance(value, dict):
            return TimeDeltaType._timedelta_to_dict(value)
        else:
            return value

    @staticmethod
    def deserialize(value, **kwargs):
        """ Convert value to timedelta """
        if isinstance(value, dict):
            try:
                return timedelta(**value)
            except:
                raise TypeError(
                    "Unable to cast value to timedelta: {}".format(value))
        else:
            return value

    @staticmethod
    def _timedelta_to_dict(td):
        if isinstance(td, timedelta):
            return {'days': td.days,
                    'seconds': td.seconds,
                    'microseconds': td.microseconds}
        elif isinstance(td, dict):
            default_td = {'days': 0,
                          'seconds': 0,
                          'microseconds': 0}
            default_td.update(td)
            return default_td
        else:
            return {}
