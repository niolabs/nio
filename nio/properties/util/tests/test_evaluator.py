from nio.properties.util.evaluator import Evaluator, InvalidEvaluationCall
from nio.signal.base import Signal
from nio.util.support.test_case import NIOTestCase


class TestEvaluator(NIOTestCase):

    def test_empty_expression(self):
        expression = ""
        evaluator = Evaluator(expression)
        result = evaluator.evaluate()
        self.assertEqual(result, '')

    def test_valid_python(self):
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

    def test_valid_signals(self):
        signal = Signal({"str": "string", "int": 42})
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
        ]
        for expression, expected_result in expressions:
            evaluator = Evaluator(expression)
            result = evaluator.evaluate(signal)
            self.assertEqual(result, expected_result)

    def test_invalid_signals(self):
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
        expression = 42
        evaluator = Evaluator(expression)
        result = evaluator.evaluate()
        self.assertEqual(result, 42)

    def test_evaluation_without_signal(self):
        expressions = [
            "{{ $ }}",
            "{{ $not_a_property }}",
            "{{ $.not_a_property }}",
        ]
        for expression in expressions:
            evaluator = Evaluator(expression)
            with self.assertRaises(InvalidEvaluationCall):
                evaluator.evaluate()
