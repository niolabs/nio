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
            # Expression properties need to be evaluated
            value = self.evaluator.evaluate(signal)
            if value is None:
                if self._property.allow_none:
                    return None
                else:
                    raise AllowNoneViolation("Property value expression is not"
                                             "allowed to evaluate to None")
            else:
                # Deserialize should not be called with None
                return self._property.deserialize(value)
        elif self.value is not None and isinstance(self.value, PropertyHolder):
            # Return property holders as they are
            return self.value
        elif self.value is not None:
            # Deserialize properties
            return self._property.deserialize(self.value)
        elif self.value is None and self._property.allow_none:
            # Return None if it is allowed
            return None
        else:
            raise AllowNoneViolation("Property value None is not allowed")
