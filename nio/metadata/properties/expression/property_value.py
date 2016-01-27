from nio.common.signal.base import Signal
from nio.metadata.properties.expression.evaluator import Evaluator


class PropertyValue:
    """ Returned when accessing properties on property holders """

    def __init__(self, instance, value):
        self.instance = instance
        self.value = value
        self.evaluator = Evaluator(str(value))

    def __call__(self, signal=None):
        return self.evaluator.evaluate(signal or Signal())
