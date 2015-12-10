from datetime import timedelta
from nio.metadata.properties.typed import TypedProperty


class TimeDeltaProperty(TypedProperty):

    """ Defines a property denoting an interval in time.

    """

    def __init__(self, **kwargs):
        super().__init__(timedelta, **kwargs)
        if "default" in kwargs and not isinstance(kwargs["default"], str):
            self._default = self.deserialize(kwargs["default"])

    def serialize(self, instance):
        value = self.__get__(instance, self.__class__)
        if isinstance(value, timedelta):
            return self._timedelta_to_dict(value)
        else:
            return value

    def _timedelta_to_dict(self, td):
        if not isinstance(td, timedelta):
            return {}

        return {
            'days': td.days,
            'seconds': td.seconds,
            'microseconds': td.microseconds
        }

    def deserialize(self, value):
        if isinstance(value, dict):
            try:
                return timedelta(**value)
            except ValueError:
                raise ValueError("Unable to cast '{0}' to a timedelta".
                                 format(value))

        return value

    @property
    def default(self):
        """Always returns a timedelta object. If the default is specified
        otherwise, then this method will deserialize it before returning.
        """
        val = self._kwargs.get("default", timedelta(0))

        if isinstance(val, timedelta):
            return val
        else:
            return self.deserialize(val)

    def get_description(self):
        """Overwrite the default with a serializable version."""
        desc = super().get_description()
        desc['default'] = self._timedelta_to_dict(self.default)
        return desc
