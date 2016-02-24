from nio.block.base import Block
from nio.util.support.test_case import NIOTestCaseNoModules
from nio.block.terminals import input, output, Terminal, TerminalType, \
    DEFAULT_TERMINAL


@input("i1", default=True)
@input("i2")
@output("o1", order=5)
@output("o2", label="parent", order=10, description="desc", default=False,
        visible=True)
class Parent(Block):
    pass


@input("ParentSubClass_input", default=True)
@output("ParentSubClass_output")
class ParentSubClass(Parent):
    pass


@input("i1")
@output("o2", label="sub", order=1)
class Duplicates(Parent):
    pass


# This class overrides both of the original terminals on Block, but doesn't
# declare a default. This is acceptable
@input("not a default")
@output("not a default")
class NoDefaultTerminals(Block):
    pass


class TestInputOutput(NIOTestCaseNoModules):

    def test_terminal_attributes(self):
        """Asserts that terminal attributes are saved and accessible """
        outputs = Terminal.get_terminals_on_class(Parent, TerminalType.output)
        parent_out2 = next(t for t in outputs if t.id == 'o2')

        self.assertEqual(parent_out2.id, "o2")
        self.assertEqual(parent_out2.label, "parent")
        self.assertEqual(parent_out2.description, "desc")
        self.assertEqual(parent_out2.order, 10)
        self.assertFalse(parent_out2.default)
        self.assertTrue(parent_out2.visible)
        # Make sure the dictionary description is correct too
        self.assertDictEqual(parent_out2.get_description(), {
            'type': 'output',
            'id': 'o2',
            'label': 'parent',
            'description': 'desc',
            'default': False,
            'visible': True,
            'order': 10
        })

    def test_terminal_default_attributes(self):
        """Asserts that default terminal attributes are saved and accessible"""
        outputs = Terminal.get_terminals_on_class(Parent, TerminalType.output)
        parent_out1 = next(t for t in outputs if t.id == 'o1')

        self.assertEqual(parent_out1.id, "o1")
        # The label should be the ID if not set
        self.assertEqual(parent_out1.label, "o1")
        self.assertEqual(parent_out1.order, 5)
        self.assertEqual(parent_out1.description, "")
        self.assertFalse(parent_out1.default)
        self.assertTrue(parent_out1.visible)
        # Make sure the dictionary description is correct too
        self.assertDictEqual(parent_out1.get_description(), {
            'type': 'output',
            'id': 'o1',
            'label': 'o1',
            'description': '',
            'default': False,
            'visible': True,
            'order': 5
        })

    def test_base_block_default_terminals(self):
        """Asserts that the base block has default terminals"""
        default_input = Terminal.get_default_terminal_on_class(
            Block, TerminalType.input)
        default_output = Terminal.get_default_terminal_on_class(
            Block, TerminalType.output)
        self.assertIsInstance(default_input, Terminal)
        self.assertIsInstance(default_output, Terminal)
        self.assertEqual(default_input.id, DEFAULT_TERMINAL)
        self.assertEqual(default_output.id, DEFAULT_TERMINAL)

    def test_no_default_terminals(self):
        """Assert that a block that defines no default terminal is allowed"""
        self.assertIsNone(Terminal.get_default_terminal_on_class(
            NoDefaultTerminals, TerminalType.input))
        self.assertIsNone(Terminal.get_default_terminal_on_class(
            NoDefaultTerminals, TerminalType.output))

    def test_sub_block_default_terminals(self):
        """Asserts that the sub block can override the parent's default"""
        default_input = Terminal.get_default_terminal_on_class(
            ParentSubClass, TerminalType.input)
        default_output = Terminal.get_default_terminal_on_class(
            ParentSubClass, TerminalType.output)
        # they overrode both input and output, but only marked the input
        # as default. This is allowed and should result in having no default
        # output
        self.assertIsInstance(default_input, Terminal)
        self.assertEqual(default_input.id, "ParentSubClass_input")
        self.assertIsNone(default_output)

    def test_terminal_inheritance(self):
        """Asserts that terminal definitions are inherited by subclasses."""
        # assert that Block has 'default' as an input attribute
        inputs = Terminal.get_terminals_on_class(Block, TerminalType.input)
        self.assert_terminals_are(inputs, [DEFAULT_TERMINAL])

        # assert that Block has 'default' as an output attribute
        outputs = Terminal.get_terminals_on_class(Block, TerminalType.output)
        self.assert_terminals_are(outputs, [DEFAULT_TERMINAL])

        # The default terminal ID should get wiped out, since we overrode
        inputs = Terminal.get_terminals_on_class(Parent, TerminalType.input)
        self.assert_terminals_are(inputs, ["i1", "i2"])

        outputs = Terminal.get_terminals_on_class(Parent, TerminalType.output)
        self.assert_terminals_are(outputs, ["o1", "o2"])

        inputs = Terminal.get_terminals_on_class(
            ParentSubClass, TerminalType.input)
        self.assert_terminals_are(
            inputs, ["i1", "i2", "ParentSubClass_input"])

        outputs = Terminal.get_terminals_on_class(
            ParentSubClass, TerminalType.output)
        self.assert_terminals_are(
            outputs, ["o1", "o2", "ParentSubClass_output"])

    def test_terminal_order(self):
        """Asserts that terminals come back in the right order"""
        outputs = Terminal.get_terminals_on_class(Parent, TerminalType.output)
        # o1 comes before o2 (5 before 10)
        self.assertEqual(outputs[0].id, "o1")
        self.assertEqual(outputs[1].id, "o2")

        subclassed_outputs = Terminal.get_terminals_on_class(
            Duplicates, TerminalType.output)
        # The subclass moved o2 first (1 before 5)
        self.assertEqual(subclassed_outputs[0].id, "o2")
        self.assertEqual(subclassed_outputs[1].id, "o1")

    def test_duplicate_terminals(self):
        """Asserts that duplicate attribute definitions use the subclass """
        inputs = Terminal.get_terminals_on_class(
            Duplicates, TerminalType.input)
        self.assert_terminals_are(inputs, ["i1", "i2"])

        outputs = Terminal.get_terminals_on_class(
            Duplicates, TerminalType.output)
        self.assert_terminals_are(outputs, ["o1", "o2"])

        # Make sure we grab our terminal properties from the sub class block
        sub_out2 = next(t for t in outputs if t.id == 'o2')
        self.assertEqual(sub_out2.label, 'sub')

    def test_terminal_types(self):
        """Asserts that terminals can only be created with TerminalType"""
        # Try to create a bad terminal
        with self.assertRaises(TypeError):
            Terminal("invalid", "fake terminal name")

        # Try to fetch a bad terminal
        with self.assertRaises(TypeError):
            Terminal.get_terminals_on_class(Block, "invalid")

        # Try to fetch a bad default terminal
        with self.assertRaises(TypeError):
            Terminal.get_default_terminal_on_class(Block, "invalid")

    def test_import_locations(self):
        """Make sure the input and output can be imported from nio.block"""
        from nio.block import input as blockInput
        from nio.block import output as blockOutput
        self.assertEqual(blockInput, input)
        self.assertEqual(blockOutput, output)

    def assert_terminals_are(self, actual_terminals, expected_terminal_ids):
        """ Asserts that a list of terminals have the expected terminal IDs """
        self.assertEqual(len(actual_terminals), len(expected_terminal_ids),
                         "Number of terminals did not match")
        for terminal in actual_terminals:
            self.assertIn(
                terminal.id, expected_terminal_ids,
                "Terminal {} found and not expected".format(terminal.id))
            expected_terminal_ids.remove(terminal.id)

        self.assertEqual(
            len(expected_terminal_ids), 0,
            "Terminal IDs {} were expected but not found".format(
                expected_terminal_ids))
