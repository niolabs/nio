from inspect import isclass
from unittest import skip

from nio.block.base import Block
from nio.testing.block_test_case import NIOBlockTestCase
from nio.signal.base import Signal
from nio.properties import BaseProperty
from nio.types import Type


class ValueSignal(Signal):

    def __init__(self, v1, v2, v3):
        super().__init__()
        self.v1 = v1
        self.V2 = v2
        self._v3 = v3

    def get_vals(self, fmt=False):
        if fmt:
            return '[{0},{1},{2}]'.format(self.v1, self.V2, self._v3)
        else:
            return '{0} {1} {2}'.format(self.v1, self.V2, self._v3)


class EvaluatorBlock(Block):
    expression = BaseProperty(Type, title="expression",
                              default='Default to {{$v1}}')


class ExprDefaultBlock(Block):
    expression = BaseProperty(Type, title="expression")


class MyCustomException(Exception):
    pass


class ExprEmptyStr(Block):
    expression = BaseProperty(Type, title="expression", default='')


class MultiExpression(Block):
    e1 = BaseProperty(Type, title="e1", default='')
    e2 = BaseProperty(Type, title="e2", default='')
    e3 = BaseProperty(Type, title="e3", default='')


class EvalSignalTestCase(NIOBlockTestCase):

    def setUp(self):
        super().setUp()
        self.signal = None
        self.default = None

    def tearDown(self):
        super().tearDown()
        self.signal = None

    def make_signal(self, v1=None, v2=None, v3=None):
        self.signal = ValueSignal(v1, v2, v3)

    def signal_test(self, expr, expected, is_expression, depends_on_signal):
        blk = EvaluatorBlock()
        self.configure_block(blk, {
            "expression": expr
        })

        if isclass(expected) and issubclass(expected, Exception):
            with self.assertRaises(expected):
                blk.expression(self.signal)
        else:
            result = blk.expression(self.signal)
            self.assertEqual(result, expected)

        # value is the raw config without being evaluated
        self.assertEqual(blk.expression.value, expr)


class TestEvalSignal(EvalSignalTestCase):

    def test_attr_not_on_signal(self):
        """Exception is raised if attribute doesn't exist on Signal."""
        blk = EvaluatorBlock()
        self.configure_block(blk, {
            "expression": "It's a {{ $foo }}"
        })
        with self.assertRaises(AttributeError):
            blk.expression(Signal({}))

    def test_default_expression(self):
        """Default property values are evaluated."""
        blk = EvaluatorBlock()
        self.configure_block(blk, {})
        self.make_signal("values")
        result = blk.expression(self.signal)
        self.assertEqual(result, "Default to values")

    def test_default_empty(self):
        """Empty expression evaluates to empty string."""
        blk = ExprEmptyStr()
        self.configure_block(blk, {})
        result = blk.expression(self.signal)
        self.assertEqual(result, '')

    def test_raw_string(self):
        """Ensure that expression evaluation passes raw strings."""
        self.signal_test("Foobar Baz Quuux", "Foobar Baz Quuux", False, False)

    def test_eval_expr(self):
        """Ensure that signals are evaluated correctly."""

        self.signal_test("{{1 + 5}}", 6, True, False)

    def test_expr_in_string(self):
        """Ensure that when an error is detected it returns None."""

        self.signal_test("{{1 + 5}} dogs went to the park",
                         "6 dogs went to the park", True, False)

    def test_multiple_expr(self):
        """One property can have multiple expressions."""

        self.signal_test("{{1 + 5}} dogs went to the {{'p'+'ark'}}",
                         "6 dogs went to the park", True, False)

    def test_signal_eval(self):
        """Ensure simple searches are allowed."""

        self.make_signal("soccer world cup")
        self.signal_test("The {{ $v1 }} is on!",
                         "The soccer world cup is on!", True, True)

    def test_multiple_signal_expr(self):
        """One property can have multiple expressions evaluated by signal."""

        self.make_signal(23, "zabow!", "sad trombone...")
        self.signal_test("When there are {{$v1}} things, "
                         "we say {{$V2 if $v1 == 23 else $_v3}}",
                         "When there are 23 things, we say zabow!", True, True)
        self.signal_test("hyphen-test-{{$v1}}-test", "hyphen-test-23-test",
                         True, True)
        self.signal.v1 = 42
        self.signal_test("When there are {{$v1}} things, "
                         "we say {{$V2 if $v1 == 23 else $_v3}}",
                         "When there are 42 things, we say sad trombone...",
                         True, True)

    def test_regex(self):
        """Ensure regular expressions are allowed."""

        self.make_signal("From amk Thu May 14 19:12:10 1998")
        self.signal_test("{{re.match(r'From\s+', $v1).group(0)}}", 'From ',
                         True, True)

    @skip("TODO: Allow access to signal attrs with numeric chars")
    def test_signal_key_as_int(self):
        """Ensure that signals are evaluated correctly."""

        self.signal = Signal({'1': 2})
        self.signal_test("{{ $1 }}", str(2), True, True)

    def test_math(self):
        """Ensure math operations are allowed."""

        self.signal_test("{{ math.sin(math.radians(90)) }}", 1.0,
                         True, False)

    def test_datetime(self):
        """Ensure datetime operations are allowed."""

        from datetime import datetime
        self.make_signal(datetime.utcnow())
        self.signal_test('{{($v1 - datetime.datetime.utcnow()).'
                         'total_seconds() < 1}}', True, True, True)

    def test_inner_dict(self):
        """Inner dictionaries need spaces before and after."""
        self.signal_test('{{ {"a": 1} }}', {"a": 1},
                         True, False)

    def test_dict_subscript(self):
        """Ensure that dictionary properties can be subscripted."""
        self.make_signal({"who": "Baron Samedi"})
        self.signal_test("Talking about {{$v1['who']}} and the Jets",
                         "Talking about Baron Samedi and the Jets", True, True)

    def test_invalid_python(self):
        """Exception is raised when the python is invalid."""
        self.make_signal(1, 2, 'string')
        self.signal_test("The value is: {{''.join([$v1,$V2])}}", TypeError,
                         True, True)
        self.signal_test("{{ print $v1 }}", SyntaxError, True, True)
        self.signal_test("{{ 1 + int($_v3) }}", ValueError, True, True)
        self.signal_test("{{ foo + str($v1) }}", NameError, True, True)

    def test_invalid_expr(self):
        """Ill-formed eval expressions are handled predictably."""
        self.signal_test("Don't close the brackets {{1 + 5",
                         "Don't close the brackets {{1 + 5",
                         False, False)

    def test_escape(self):
        """Signals and curly braces can be escaped."""
        self.make_signal('zero')
        self.signal_test("We want {{'\$three and \{{ %s \}} cents' % $v1}}",
                         "We want $three and {{ zero }} cents", True, True)
        self.signal_test("Please {{ 'evaluate this' }} $not_a_signal",
                         "Please evaluate this $not_a_signal", True, False)
        self.signal_test("Please {{ 'evaluate this' }} $not_a_signal",
                         "Please evaluate this $not_a_signal", True, True)
        # Do not escape since it's not a real expression without the escape
        self.signal_test("Please $don't \{{ evaluate this",
                         "Please $don't \{{ evaluate this", False, False)
        # Use escape character if curly braces would otherwise be an expression
        self.signal_test("Please $don't \{{ evaluate this }}",
                         "Please $don't {{ evaluate this }}", False, False)
        self.signal_test("Please $don't \{{ evaluate this }}",
                         "Please $don't {{ evaluate this }}", True, True)

    def test_method_call(self):
        """Methods on signals can be called."""
        self.make_signal('foo', 'bar', 'baz')
        self.signal_test("A list of values: {{$get_vals(True)}}",
                         "A list of values: [foo,bar,baz]", True, True)
        self.signal_test("A list of values: {{$get_vals()}}",
                         "A list of values: foo bar baz", True, True)

    def test_returns_list(self):
        """List expressions return list."""
        self.make_signal([1, 2, 3])
        self.signal_test("{{['a', 'b', 'c', 'easy as'] + $v1}}",
                         ['a', 'b', 'c', 'easy as', 1, 2, 3], True, True)

    def test_return_signal(self):
        """Signal can be retrieved with $."""
        self.make_signal([1, 2, 3])
        self.signal_test("{{$}}", self.signal, True, True)

    def test_hasattr(self):
        """Expressions support hasattr on signals."""
        self.make_signal(1, 2, 3)
        self.signal_test("{{hasattr($, 'v1')}}", True, True, True)
        self.signal_test("{{hasattr($, 'baz')}}", False, True, True)

    def test_direct_attr_ref(self):
        """Signals attrs can be reference with . notation."""
        self.make_signal(1)
        self.signal_test("I want {{$.v1}}", "I want 1", True, True)

        # this kind of access is dangerous!!
        with self.assertRaises(AttributeError):
            self.signal_test("I want {{$.v4}}", "Won't work", True, True)

        # this isn't a lexically valid attribute name, so, direct
        # substitution of str('signal') is performed, resulting in
        # a name error ('signal1v' is not defined)
        with self.assertRaises(NameError):
            self.signal_test("{{$1v}}", "stuff", True, True)

    def test_random(self):
        """Ensure import on the fly is allowed."""
        self.signal_test("{{__import__('random').randint(1,1)}}", 1,
                         True, False)

    def test_no_cache_collision(self):
        """Make sure espression caches don't override each other."""
        self.make_signal(1)
        blk = MultiExpression()
        self.configure_block(blk, {
            "e1": "{{ $v1 }}",
            "e2": "{{ $noexist }}",
            "e3": "{{ 'string' }}"
        })
        self.assertEqual(blk.e1(self.signal), 1)
        with self.assertRaises(Exception):
            blk.e2(self.signal)
        self.assertEqual(blk.e3(self.signal), 'string')

    def test_sub_dicts(self):
        """Make sure if a signal contains a dict it's subscriptable."""
        blk = ExprDefaultBlock()
        self.configure_block(blk, {
            "expression": "{{ $v1['a'] }}"
        })
        self.make_signal({'a': 1, 'b': 2})
        self.assertEqual(blk.expression(self.signal), 1)
