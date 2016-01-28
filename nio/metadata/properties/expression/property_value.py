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
        if not self.is_expression():
            # The value doesn't need to be vaildated if it's an expression
            self._property.deserialize(self.value)
        # Check if we are setting None if that's now allowed
        if not self._property.kwargs["allow_none"] and self.value is None:
            raise AllowNoneViolation

    def is_expression(self):
        # TODO: this code should not be both here and in evaluator
        try:
            return "{{" in self.value and \
                    "}}" in self.value
        except:
            return False

    def __call__(self, signal=None):
        """ Return value, evaluated if it is an expression """
        if isinstance(self.value, str):
            value = self.evaluator.evaluate(signal or Signal())
            return self._property.deserialize(value)
        elif self.value is not None or self._property.kwargs["allow_none"]:
            return self.value
        elif self.value is None and self._property.kwargs["allow_none"]:
            return self.value
        else:
            raise Exception("Property value None is not allowed")

