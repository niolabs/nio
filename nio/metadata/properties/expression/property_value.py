from nio.common.signal.base import Signal
from nio.metadata.properties.exceptions import AllowNoneViolation
from nio.metadata.properties.expression.evaluator import Evaluator


class PropertyValue:
    """ Returned when accessing properties on property holders """

    def __init__(self, property, value=None, validate=True):
        self._property = property
        self.value = value
        if validate:
            self._validate_value()
        self.evaluator = Evaluator(str(value))

    def _validate_value(self):
        # Check that the value is the correct type
        self._property.deserialize(self.value, **self._property.kwargs)
        # Check if we are setting None if that's now allowed
        if not self._property.allow_none and self.value is None:
            raise AllowNoneViolation

    def __call__(self, signal=None):
        """ Return value, evaluated if it is an expression """
        from nio.metadata.properties.holder import PropertyHolder
        if isinstance(self.value, str):
            # Evaluate and deserialize string since they might be expressions
            value = self.evaluator.evaluate(signal or Signal())
            return self._property.deserialize(value, **self._property.kwargs)
        elif self.value is not None and isinstance(self.value, PropertyHolder):
            # Return property holders as they are
            return self.value
        elif self.value is not None:
            # Deserialize properties
            return self._property.deserialize(self.value,
                                            **self._property.kwargs)
        elif self.value is None and self._property.allow_none:
            # Return None if it is allowed
            return None
        else:
            raise Exception("Property value None is not allowed")
