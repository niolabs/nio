import re

from nio.properties.exceptions import InvalidEvaluationCall
from nio.properties.util.parser import Parser
from nio.signal.base import Signal


class TemporarySignal(Signal):

    def __getattribute__(self, name):
        raise InvalidEvaluationCall


class Evaluator:

    """ Evaluate python expressions against a Signal.

    Class for transforming NIO's dynamic signal access mini-language
    into valid Python.

    Creates a new parser object each time 'evaluate' is called (i.e. for each
    incoming signal).

    Args:
        expression (str): The string or expression to be interpolated or
            evaluated. If expression is not a string then the raw expression
            is returned when evaluated.

    Raises:
        Exception: Raise any python exception during evaluation

    """
    delimiter = re.compile(r'(?<!\\)({{|}})|(\s)')
    expression_cache = {}

    def __init__(self, expression):
        self.expression = expression

    def evaluate(self, signal=None):
        if not isinstance(self.expression, str):
            return self.expression
        cache_key = (self.expression)
        parsed = self.__class__.expression_cache.get(cache_key, None)
        if parsed is None:
            # Only parse the expression if we haven't already done it.
            tokens = self.tokenize(self.expression)
            parser = Parser()
            parsed = parser.parse(tokens)
            self.__class__.expression_cache[cache_key] = parsed
        try:
            result = self._eval(signal, parsed)
            result_len = len(result)
            if result_len > 1:
                result = ''.join([str(o) for o in result])
            elif result_len == 1:
                result = result[0]
            else:
                result = ''
        except:
            raise

        return result

    def _eval(self, signal, parsed):
        result = []
        for item in parsed:
            if hasattr(item, '__call__'):
                if signal is None:
                    # Use a temporary signal that raises InvalidEvaluationCall
                    signal = TemporarySignal()
                # Evaluate the expression against the signal
                item = item(signal, self)
                if isinstance(item, TemporarySignal):
                    # This is to catch evaluating the expression "{{ $ }}"
                    # when evaluated without a Signal
                    raise InvalidEvaluationCall
            result.append(item)
        return result

    def tokenize(self, expression):
        """ Pad the delimiters with whitespace and split the expression. """
        tokens = self.delimiter.split(expression)

        # the split includes a bunch of None's and empty strings...
        return [t for t in tokens if t]
