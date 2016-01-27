import inspect
import re
from nio.metadata.properties.expression.parser import Parser


class Evaluator:

    """ Class for transforming NIO's dynamic signal access mini-language
    into valid Python.

    Creates a new parser object each time 'evaluate' is called (i.e. for each
    incoming signal).

    Args:
        expression (str): The string or expression to be interpolated or
            evaluated.
        default (ANY): The default value for non-existent attributes.

    Raises:
        Exception: If an expression is evaluated and it tries to get an
            attribute on a signal when that attribute doesn't exist.

    """
    delimiter = re.compile(r'(?<!\\)({{|}})|(\s)')
    expression_cache = {}

    def __init__(self, expression):
        self.expression = expression

    def evaluate(self, signal):
        cache_key = (self.expression)
        parsed = self.__class__.expression_cache.get(cache_key, None)
        if parsed is None:
            # Only parse the expression if we haven't already done it.
            if self.is_expression():
                tokens = self.tokenize(self.expression)
                parser = Parser()
                parsed = parser.parse(tokens)
            else:
                parsed = self.expression
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
                item = item(signal, self)
            result.append(item)
        return result

    def tokenize(self, expression):
        """ Pad the (unescaped) delimiters with whitespace and split
        the expression.

        """
        tokens = self.delimiter.split(expression)

        # the split includes a bunch of None's and empty strings...
        return [t for t in tokens if t]

    def is_expression(self):
        return "{{" in self.expression and \
                "}}" in self.expression

    def depends_on_signal(self):
        return "$" in self.expression and self.is_expression()
