from nio.metadata.properties.typed import TypedProperty
from nio.metadata.properties.expression_util import Evaluator


class ExprFunc(str):

    def __init__(self, *args, **kwargs):
        self._object = args[0]

    def init(self, attr_default=''):
        # TODO: Evaluator needs the default but how to pass it into here??
        self.evaluator = Evaluator(self._object, attr_default)
        self.default = attr_default

    def __call__(self, signal):
        return self.evaluator.evaluate(signal)

    def is_expression(self):
        return "{{" in self.evaluator.expression and \
                "}}" in self.evaluator.expression

    def depends_on_signal(self):
        return "$" in self.evaluator.expression and self.is_expression()

    def get_expression(self):
        return self.evaluator.expression


class StringProperty(TypedProperty):
    """ Defines a property for a string type

    """

    def __init__(self, **kwargs):
        super().__init__(str, **kwargs)

    def deserialize(self, value):
        try:
            return str(value)
        except ValueError:
            raise ValueError("Unable to cast '{0}' to a string".format(value))

    def __get__(self, instance, cls):
        # In case we use the default, it also needs to be an ExprFunc
        default = ExprFunc(self._default)
        default.init(self._kwargs.get('attr_default', ''))
        return self._values.get(instance, default)

    def __set__(self, instance, value):
        self._check_allow_none(value)
        if value is not None and not isinstance(value, self._type):
            raise TypeError("Must be a {0}".format(self._type))
        # Save an ExprFunc instead of just the regular str
        self._values[instance] = ExprFunc(value)
        self._values[instance].init(self._kwargs.get('attr_default', ''))
