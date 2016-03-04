import datetime
import math
import re


class Parser:

    """ Helper class for translation and evaluation of nio expressions

    Args:
        signal (Signal): Contextualizes incoming code snippets.
        default (ANY): If an incoming signal does not have the
            requested attribute, this value is interpolated instead.

    """
    escaped = re.compile(r'\\(\$|{{|}})')
    ident = re.compile(r'(?<!\\)\$([_A-Za-z]([_A-Za-z0-9])*)?|[^\$]*')
    ident_stem = re.compile(r'[_a-zA-Z][_a-zA-Z0-9]*$')

    def parse(self, tokens):
        """ Parse a list of tokens and evaluate them.

        Traverses the 'AST' (list of tokens) recursively, transforming,
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
        """ Build a function that evaluates an expression.

        Helper function to transform incoming expressions and wrap
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
                result = 'getattr(signal,"{0}")'.format(tok[1])

        return result
