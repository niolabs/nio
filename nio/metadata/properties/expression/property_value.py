from nio.common.signal.base import Signal
from nio.metadata.properties.expression.evaluator import Evaluator


class PropertyValue:
    """ Returned when accessing properties on property holders """

    def __init__(self, property, value=None):
        self._property = property
        self.value = value
        self.evaluator = Evaluator(str(value))

    def __call__(self, signal=None):
        """ Return value, evaluated if it is an expression """
        if isinstance(self.value, str):
            # TODO: this should deserialize to return the proper type
            # Then the PropertyValue needs to know its type?
            return self.evaluator.evaluate(signal or Signal())
        elif self.value is not None or self._property.kwargs["allow_none"]:
            return self.value
        else:
            raise Exception("Property value None is not allowed")

