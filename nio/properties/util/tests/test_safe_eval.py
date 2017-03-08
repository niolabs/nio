from unittest.mock import patch

from nio.properties.util.evaluator import Evaluator
from nio.properties.util.safe_eval import SafeEval
from nio.signal.base import Signal
from nio.testing.test_case import NIOTestCaseNoModules


class TestSafeEval(NIOTestCaseNoModules):

    def setUp(self):
        super().setUp()
        SafeEval._mapping = None

    def tearDown(self):
        super().tearDown()
        SafeEval._mapping = None

    def test_allowed_modules(self):
        """ Asserts operations can only reference allowed modules

        This tests starts with default allowed modules and then modifies it
        to verify that a call using a 'removed' module is not allowed
        """

        # by default, both random and math are allowed
        signal = Signal({'two': 2})
        expression = "{{ random.randrange(1, $.two) }}"
        evaluator = Evaluator(expression)
        result = evaluator.evaluate(signal)
        self.assertEqual(result, 1)

        expression = "{{ math.ceil(1.8) }}"
        evaluator = Evaluator(expression)
        result = evaluator.evaluate(signal)
        self.assertEqual(result, 2)

        # set modules to allow math operations only
        SafeEval.set_modules(['math'])

        # verify an expression containing a not-allowed module fails
        expression = "{{ random.randrange(1, $.two) }}"
        evaluator = Evaluator(expression)
        with self.assertRaises(TypeError):
            evaluator.evaluate(signal)

        # verify that math operations are ok
        expression = "{{ math.ceil(1.8) }}"
        evaluator = Evaluator(expression)
        result = evaluator.evaluate(signal)
        self.assertEqual(result, 2)

    def test_build_locals_mapping(self):
        """ Assert that locals_mapping is only built when needed
        """
        expression = "{{ 'hello' }}"
        with patch.object(SafeEval, "_build_locals_mapping") as patched_build:
            self.assertEqual(patched_build.call_count, 0)
            evaluator = Evaluator(expression)
            evaluator.evaluate(None)
            self.assertEqual(patched_build.call_count, 1)

            # evaluate again and assert that '_build_locals_mapping'
            # was not called this time
            evaluator.evaluate(None)
            self.assertEqual(patched_build.call_count, 1)

    def test_restrictions(self):
        """ Asserts some known restrictions
        """
        expression = "{{__import__('random').randint(1,1)}}"
        evaluator = Evaluator(expression)
        with self.assertRaises(TypeError):
            evaluator.evaluate(None)

        expression = "{{os.name}}"
        evaluator = Evaluator(expression)
        with self.assertRaises(TypeError):
            evaluator.evaluate(None)
