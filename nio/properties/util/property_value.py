from nio.signal.base import Signal
from nio.properties.exceptions import AllowNoneViolation
from nio.properties.util.evaluator import Evaluator


class PropertyValue:
    """ Returned when accessing properties on property holders

    PropertyValues are callable and return the deserialized value of the
    property. If the value is a string that is a valied n.io expression, it
    is first evaluated, optionally against a Signal.

    """

    def __init__(self, property, value=None):
        self._property = property
        self.value = value
        self.evaluator = Evaluator(str(value))

    def __call__(self, signal=None):
        """ Return value, evaluated if it is an expression """
        from nio.properties import PropertyHolder
        if self._property.is_expression(self.value):
            # Evaluate and deserialize string since they might be expressions
            value = self.evaluator.evaluate(signal or Signal())
            # TODO: why pass kwargs? shouldn't the property already know?
            return self._property.deserialize(value, **self._property.kwargs)
        elif self.value is not None and isinstance(self.value, PropertyHolder):
            # Return property holders as they are
            return self.value
        elif self.value is not None:
            # Deserialize properties
            # TODO: why pass kwargs? shouldn't the property already know?
            return self._property.deserialize(self.value,
                                              **self._property.kwargs)
        elif self.value is None and self._property.allow_none:
            # Return None if it is allowed
            return None
        else:
            raise Exception("Property value None is not allowed")
