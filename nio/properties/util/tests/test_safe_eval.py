from unittest.mock import patch

from nio.properties.util.evaluator import Evaluator
from nio.properties.util.safe_eval import SafeEval
from nio.signal.base import Signal
from nio.testing.test_case import NIOTestCaseNoModules


class TestSafeEval(NIOTestCaseNoModules):

    def tearDown(self):
        # restore default modules
        SafeEval.set_modules(["datetime", "json", "math", "random",
                              "re", "struct"])
        super().tearDown()

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
        with patch.object(SafeEval, "_build_eval_args") as patched_build:
            patched_build.return_value = {}, {}
            self.assertEqual(patched_build.call_count, 0)
            evaluator = Evaluator(expression)
            evaluator.evaluate(None)
            self.assertEqual(patched_build.call_count, 1)

            # evaluate again and assert that '_build_eval_args'
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

        expression = "{{for something}}"
        evaluator = Evaluator(expression)
        with self.assertRaises(SyntaxError):
            evaluator.evaluate(None)

    def test_expressions(self):
        """ Asserts expressions encountered in production environments
        """

        expression = "{{float(1.2)}}"
        evaluator = Evaluator(expression)
        result = evaluator.evaluate(None)
        self.assertEqual(result, 1.2)

        data = {"type": "D",
                "name": "name",
                "zone": "zone",
                "group": "group",
                "units": "units"}
        signal = Signal(data)
        expression = \
            "{{[{" \
            "'terminal': x+1, " \
            "'type': y[0], " \
            "'name': y[1] if y[1] != '_' else None, " \
            "'zone': y[2] if y[2] != '_' else None, " \
            "'group': y[3] if y[3] != '_' else None, " \
            "'units': y[4] if y[4] != '_' else None, " \
            "'limits': {'lolo': None, 'lo': None, 'hi': None, 'hihi': None} } "\
            "for x,y in enumerate(zip($type, $name, $zone, $group, $units)) " \
            "if y[0] == 'D'] }}"
        evaluator = Evaluator(expression)
        result = evaluator.evaluate(signal)
        self.assertTrue(result[0]['group'], 'group')
        self.assertTrue(isinstance(result[0]['limits'], dict))

        data = {"type": "A",
                "name": "name",
                "zone": "zone",
                "group": "group",
                "min": "1",
                "max": "2",
                "units": "D",
                "lolo": "1.1",
                "lo": "3",
                "hi": "4",
                "hihi": "5",
                }
        signal = Signal(data)
        expression = \
            "{{ [{" \
            "'terminal': x+1, " \
            "'type': y[0], " \
            "'name': y[1] if y[1] != '_' else None, " \
            "'min': float(y[2]) if y[2].split('.')[0].isdigit() else 0, " \
            "'max': float(y[3]) if y[3].split('.')[0].isdigit() else 0, " \
            "'zone' : y[4] if y[4] != '_' else None,  " \
            "'group': y[5] if y[5] != '_' else None, " \
            "'units': y[6] if y[6] != '_' else None, " \
            "'limits': {'lolo': float(y[7]) if y[7] != '_' else None, " \
            "'lo': float(y[8]) if y[8] != '_' else None, " \
            "'hi': float(y[9]) if y[9] != '_' else None, " \
            "'hihi': float(y[10]) if y[10] != '_' else None} } " \
            "for x,y in enumerate(zip($type, $name, $min, $max, $zone, $group,"\
            "$units, $lolo, $lo, $hi, $hihi)) if y[0] == 'A'] }}"
        evaluator = Evaluator(expression)
        result = evaluator.evaluate(signal)
        self.assertTrue(result[0]['zone'], 'zone')
        self.assertTrue(result[0]['limits']['lolo'], 1.1)
        self.assertTrue(isinstance(result[0]['limits'], dict))

        expression = \
            "{{ [{" \
            "'terminal': x+1, " \
            "'type': y[0], " \
            "'name': y[1] if y[1] != '_' else None, " \
            "'min': float(y[2]) if y[2].split('.')[0].isdigit() else 0, " \
            "'max': float(y[3]) if y[3].split('.')[0].isdigit() else 0, " \
            "'zone' : y[4] if y[4] != '_' else None,  " \
            "'group': y[5] if y[5] != '_' else None, " \
            "'units': y[6] if y[6] != '_' else None, " \
            "'limits': float(y[7]) if y[7] != '_' else None, " \
            " } " \
            "for x,y in enumerate(zip($type, $name, $min, $max, $zone, $group,"\
            "$units, $lolo, $lo, $hi, $hihi)) if y[0] == 'A'] }}"
        evaluator = Evaluator(expression)
        result = evaluator.evaluate(signal)
        self.assertEqual(result[0]['min'], 1)
        self.assertEqual(result[0]['max'], 2)

        data = {"type": "T",
                "name": "name",
                "zone": "zone",
                "group": "group",
                "min": "1",
                "max": "2",
                "units": "units",
                "lolo": "1",
                "lo": "2",
                "hi": "3",
                "hihi": "4",
                }
        signal = Signal(data)
        expression = \
            "{{[{'terminal': x + 1, " \
            "'type': y[0], " \
            "'name': y[1] if y[1] != '_' else None," \
            "'zone': y[2] if y[2] != '_' else None," \
            "'group': y[3] if y[3] != '_' else None," \
            "'units': y[4] if y[4] != '_' else None," \
            "'limits': {" \
                "'lolo': float(y[5]) if y[5] != '_' else None," \
                "'lo': float(y[6]) if y[6] != '_' else None, " \
                "'hi': float(y[7]) if y[7] != '_' else None, "\
                "'hihi': float(y[8]) if y[8] != '_' else None } } "\
            "for x, y in enumerate(zip($type, $name, $zone, $group, $units, " \
            "$lolo, $lo, $hi, $hihi)) if y[0] == 'T']}}"

        evaluator = Evaluator(expression)
        result = evaluator.evaluate(signal)
        self.assertEqual(result[0]['limits']['lolo'], 1)

        signal = Signal({'cond': True})

        # assert reference to a signal attr
        expression = "{{$.cond if $.cond else None}}"
        evaluator = Evaluator(expression)
        result = evaluator.evaluate(signal)
        self.assertTrue(result)

        # assert reference to a signal attr within dict, it turns out that
        # the signal reference that is used is the one defined in globals
        expression = "{{[{'entry': math.fabs(i) if $.cond else None} " \
                     "for i in [1]]}}"
        evaluator = Evaluator(expression)
        result = evaluator.evaluate(signal)
        self.assertEqual(len(result), 1)
        self.assertDictEqual(result[0], {'entry': 1})

        # assert reference to a module function
        expression = "{{[{'entry': math.fabs(i) if 1 else None} for i in [1]]}}"
        evaluator = Evaluator(expression)
        result = evaluator.evaluate(signal)
        self.assertEqual(len(result), 1)
        self.assertDictEqual(result[0], {'entry': 1})

        # assert reference to a builtin function
        expression = "{{[{'entry': abs(i) if 1 else None} for i in [1]]}}"
        evaluator = Evaluator(expression)
        result = evaluator.evaluate(signal)
        self.assertEqual(len(result), 1)
        self.assertDictEqual(result[0], {'entry': 1})

        # assert hasattr
        expression = "{{ hasattr($, 'cond') }}"
        evaluator = Evaluator(expression)
        result = evaluator.evaluate(signal)
        self.assertEqual(result, True)

        # assert type, dict
        expression = "{{ type($cond) == type(dict()) }}"
        evaluator = Evaluator(expression)
        result = evaluator.evaluate(signal)
        self.assertEqual(result, False)

        # bool conversion grabbing from a dict within signal
        signal = Signal({'value': {'pre_weight': 0}})
        expression = "{{ bool($value.get('pre_weight')) }}"
        evaluator = Evaluator(expression)
        result = evaluator.evaluate(signal)
        self.assertEqual(result, False)

        # an expression with a double 'for' statement
        signal = Signal({'packet': [0x1F, 0x2F, 0x3F, 0x4F, 0x5F,
                                    0x6F, 0x7F, 0x8F, 0x9F, 0xAF,
                                    0xBF, 0xCF, 0xDF, 0xFF]})
        expression = "{{ $packet[10] == 0xFF - (sum([n & 0x0F " \
                     "for n in $packet[1:10]]) + sum([n >> 4 " \
                     "for n in $packet[1:10]])) }}"
        evaluator = Evaluator(expression)
        result = evaluator.evaluate(signal)
        self.assertEqual(result, False)
