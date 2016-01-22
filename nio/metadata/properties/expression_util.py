import re
import inspect
import datetime
import math
import json


class Parser:

    """ Helper class for translation and evaluation of incoming
    nio scripts.

    Args:
        signal (Signal): Contextualizes incoming code snippets.
        default (ANY): If an incoming signal does not have the
            requested attribute, this value is interpolated instead.

    """
    escaped = re.compile(r'\\(\$|{{|}})')
    ident = re.compile(r'(?<!\\)\$([_A-Za-z]([_A-Za-z0-9])*)?|[^\$]*')
    ident_stem = re.compile(r'[_a-zA-Z][_a-zA-Z0-9]*$')

    def __init__(self, default, raises):
        self.default = default
        self.raises_except = raises

    def parse(self, tokens):
        """ Traverses the 'AST' (list of tokens) recursively, transforming,
        ignoring, or evaluating them as needed.

        Args:
            tokens (list(str)): Tokens corresponding to the expression
                being evaluated.

        """
        expr = ''
        if not tokens:
            result = []
        elif tokens[0] == '{{':
            tokens.pop(0)

            # Gobble up tokens until the closing delimiter
            while tokens[0] != '}}':
                expr += tokens.pop(0)
                if len(tokens) == 0:
                    raise SyntaxError("Unexpected EOF while parsing")
            tokens.pop(0)

            result = self._build_function(expr) + self.parse(tokens)
        else:

            # Just a raw string. Remove any escape characters and
            # move on.
            _next = self.escaped.sub(self._unescape, tokens.pop(0))
            result = [_next] + self.parse(tokens)

        return result

    def _build_function(self, expr):
        """ Helper function to transform incoming expressions and wrap
        them in unnamed functions. This leaves the expressions themselves
        compiled and ready to be parameterized with incoming signals
        """
        transformed = self.ident.sub(self._transform_attr, expr)
        unescaped = self.escaped.sub(self._unescape, transformed)
        try:
            return [eval("lambda signal, self: {}".format(unescaped))]
        except Exception as e:
            _type = type(e)
            raise _type(
                "Error while evaluating {}: {}".format(unescaped, str(e))
            )

    def _unescape(self, match):
        return match.group(0)[1:]

    def _transform_attr(self, match):
        tok = match.group(0).split('$')
        result = tok[0]
        if not result:
            # grab the signal
            result = 'signal'

            # if the rest of the token is a valid identifier, generate code to
            # get the corresponding attribute. otherwise just return the signal
            if self.ident_stem.match(tok[1]) is not None:
                if self.raises_except:
                    result = 'getattr(signal,"{0}")'.format(tok[1])
                else:
                    result = 'getattr(signal, "{0}", self.default)'. \
                        format(tok[1])

        return result


class Evaluator:

    """ Class for transforming NIO's dynamic signal access mini-language
    into valid Python.

    Creates a new parser object each time 'evaluate' is called (i.e. for each
    incoming signal).

    Args:
        expression (str): The string or expression to be interpolated or
            evaluated.
        default (ANY): The default value for non-existent attributes.

    """
    delimiter = re.compile(r'(?<!\\)({{|}})|(\s)')
    expression_cache = {}

    def __init__(self, expression, default):
        self.default = default
        self.raises_except = inspect.isclass(self.default) and \
            issubclass(self.default, Exception)
        self.expression = expression

    def _raise(self, e):
        raise e

    def evaluate(self, signal):
        cache_key = (self.expression, self.default)
        parsed = self.__class__.expression_cache.get(cache_key, None)
        if parsed is None:
            tokens = self.tokenize(self.expression)
            parser = Parser(self.default, self.raises_except)
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
                if self.raises_except:
                    raise self.default()
                result = self.default
        except:
            if self.raises_except:
                # raise 'custom' exception
                raise self.default()
            # re-raise same otherwise
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
