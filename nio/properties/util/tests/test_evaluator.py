import types
from unittest.mock import patch

from nio.properties.exceptions import InvalidEvaluationCall
from nio.properties.util.evaluator import Evaluator
from nio.signal.base import Signal
from nio.testing.test_case import NIOTestCaseNoModules


class TestEvaluator(NIOTestCaseNoModules):

    def test_empty_expression(self):
        """Empty expressions evaluate to empty string."""
        expression = ""
        evaluator = Evaluator(expression)
        result = evaluator.evaluate()
        self.assertEqual(result, '')

    def test_valid_python(self):
        """Valid expressions return the correct value."""
        expressions = [
            ("{{ 'hello' }}",
             'hello'),
            ("{{ print('world') }}",
             None),
            ("{{ 1 + 2 }}",
             3),
        ]
        for expression, expected_result in expressions:
            evaluator = Evaluator(expression)
            result = evaluator.evaluate()
            self.assertEqual(result, expected_result)

    def test_invalid_python(self):
        """Exceptions are raised when expressions are invalid python."""
        signal = Signal({"str": "string", "int": 42})
        expressions = [
            "{{ 'str' + 42 }}",
            "{{ 1 + 'string' }}",
        ]
        for expression in expressions:
            evaluator = Evaluator(expression)
            with self.assertRaises(Exception):
                evaluator.evaluate(signal)

    def test_valid_signals(self):
        """Valid expressions with signals return the correct value."""
        signal = Signal({"str": "string", "int": 42, "bool": False})
        expressions = [
            ("{{ $ }}",
             signal),
            ("{{ $to_dict() }}",
             signal.to_dict()),
            ("{{ $str }}",
             'string'),
            ("{{ $.str }}",
             'string'),
            ("{{ $int }}",
             42),
            ("{{ $.int }}",
             42),
            ("{{$.str}},{{$.int}}",
             'string,42'),
            ("{{ $.bool == False }}",
             True),
            ("{{ $.bool }}",
             False)
        ]
        for expression, expected_result in expressions:
            evaluator = Evaluator(expression)
            result = evaluator.evaluate(signal)
            self.assertEqual(result, expected_result)

    def test_invalid_signals(self):
        """Exceptions are raised when signal expressions are invalid python."""
        signal = Signal({"str": "string", "int": 42})
        expressions = [
            "{{ $str + 42 }}",
            "{{ $int + 'string' }}",
            "{{ $not_a_property }}",
            "{{ $.not_a_property }}",
        ]
        for expression in expressions:
            evaluator = Evaluator(expression)
            with self.assertRaises(Exception):
                evaluator.evaluate(signal)

    def test_expression_that_is_not_a_string(self):
        """Expressions don't need to be strings.

        If an expression is not a string then it returns the raw value.

        """

        expression = 42
        evaluator = Evaluator(expression)
        result = evaluator.evaluate()
        self.assertEqual(result, 42)

    def test_evaluation_without_signal(self):
        """InvalidEvaluationCall is raised if signal is not present."""
        expressions = [
            "{{ $ }}",
            "{{ $not_a_property }}",
            "{{ $.not_a_property }}",
        ]
        for expression in expressions:
            evaluator = Evaluator(expression)
            with self.assertRaises(InvalidEvaluationCall):
                evaluator.evaluate()

    def test_imported_libraries(self):
        """Certain libraries should be able to be used in expressions."""
        expressions = [
            "{{ datetime }}",
            "{{ json }}",
            "{{ math }}",
            "{{ random }}",
            "{{ re }}",
            "{{ struct }}"
        ]
        for expression in expressions:
            evaluator = Evaluator(expression)
            self.assertTrue(isinstance(evaluator.evaluate(), types.ModuleType))

    def test_modules_usage(self):
        """Valid expressions asserting library usage syntax."""
        signal = Signal({'two': 2})
        expressions = [
            ("{{ random.randrange(1, 2) }}",
             1),
            ("{{ math.ceil(1.8) }}",
             2),
        ]
        for expression, expected_result in expressions:
            evaluator = Evaluator(expression)
            result = evaluator.evaluate(signal)
            self.assertEqual(result, expected_result)

    def test_expression_cache(self):
        # assert that parser is invoked ONLY once for the same expression
        with patch("nio.properties.util.evaluator.Parser") as parser_mock:
            evaluator = Evaluator("{{'hello1'}}")
            evaluator.evaluate(None)
            self.assertEqual(parser_mock.call_count, 1)
            # evaluate again and verify parser was not invoked again
            evaluator.evaluate(None)
            self.assertEqual(parser_mock.call_count, 1)

            # change expression, and verify that parser was invoked
            evaluator = Evaluator("{{'hello2'}}")
            evaluator.evaluate(None)
            self.assertEqual(parser_mock.call_count, 2)

            # go back to former expression and verify its parsing
            # is still cached
            evaluator = Evaluator("{{'hello1'}}")
            evaluator.evaluate(None)
            self.assertEqual(parser_mock.call_count, 2)
