from nio.common.block.base import Block
from nio.util.support.test_case import NIOTestCaseNoModules
from nio.common.block.attribute.input_output import get_class_attributes, \
    Input, Output


@Input("i1")
@Input("i2")
@Output("o1")
@Output("o2")
class Parent(Block):
    pass


@Input("ParentSubClass_input")
@Output("ParentSubClass_output")
class ParentSubClass(Parent):
    pass


@Input("i1")
@Output("o2")
class Duplicates(Parent):
    pass


class NoInputsOutputs(Block):
    pass


@Input("only_input")
class OneInputClass(Block):
    pass


@Output("only_output")
class OneOutputClass(Block):
    pass


@Input("default")
@Input("another_input")
class UserInputDefaultClass(Block):
    pass


@Output("default")
@Output("another_output")
class UserOutputDefaultClass(Block):
    pass


@Input("default")
@Input("another_input")
@Output("default")
@Output("another_output")
class UserDefaultsClass(Block):
    pass


class TestInputOutput(NIOTestCaseNoModules):

    def test_class_attribute(self):
        """ Asserts that get_class_attribute returns attributes as expected
        """

        # assert that Block has 'default' as an input attribute
        inputs = Input.get_class_attribute(Block)
        self._assert_inclusions(inputs, ["default"])

        # assert that Block has 'default' as an output attribute
        outputs = Output.get_class_attribute(Block)
        self._assert_inclusions(outputs, ["default"])

        inputs = Input.get_class_attribute(Parent)
        self._assert_inclusions(inputs, ["i1", "i2"])

        outputs = Output.get_class_attribute(Parent)
        self._assert_inclusions(outputs, ["o1", "o2"])

        inputs = Input.get_class_attribute(ParentSubClass)
        self._assert_inclusions(inputs, ["i1", "i2", "ParentSubClass_input"])

        outputs = Output.get_class_attribute(ParentSubClass)
        self._assert_inclusions(outputs, ["o1", "o2", "ParentSubClass_output"])

    def test_class_attributes(self):
        """ Asserts that get_class_attributes returns attributes as expected
        """

        # assert that input and output have 'default' at the Block level
        attributes = get_class_attributes(Block)
        self.assertEqual(len(attributes), 2)

        self.assertIn("input", attributes)
        inputs = attributes["input"]
        self._assert_inclusions(inputs, ["default"])

        self.assertIn("output", attributes)
        outputs = attributes["output"]
        self._assert_inclusions(outputs, ["default"])

        attributes = get_class_attributes(Parent)
        self.assertEqual(len(attributes), 2)

        self.assertIn("input", attributes)
        inputs = attributes["input"]
        self._assert_inclusions(inputs, ["i1", "i2"])

        self.assertIn("output", attributes)
        outputs = attributes["output"]
        self._assert_inclusions(outputs, ["o1", "o2"])

    def test_duplicates_class_attribute(self):
        """ Asserts that duplicate attribute definitions are removed when
        calling get_class_attribute
        """
        inputs = Input.get_class_attribute(Duplicates)
        self._assert_inclusions(inputs, ["i1", "i2"])

        outputs = Output.get_class_attribute(Duplicates)
        self._assert_inclusions(outputs, ["o1", "o2"])

    def test_duplicates_class_attributes(self):
        """ Asserts that duplicate attribute definitions are removed when
        calling get_class_attributes
        """

        attributes = get_class_attributes(Duplicates)
        self.assertEqual(len(attributes), 2)

        self.assertIn("input", attributes)
        inputs = attributes["input"]
        self._assert_inclusions(inputs, ["i1", "i2"])

        self.assertIn("output", attributes)
        outputs = attributes["output"]
        self._assert_inclusions(outputs, ["o1", "o2"])

    def test_no_inputs_no_outputs(self):
        """ Asserts that properties are not cached from call to call
        """

        attributes = get_class_attributes(Parent)
        self.assertEqual(len(attributes), 2)

        self.assertIn("input", attributes)
        inputs = attributes["input"]
        self._assert_inclusions(inputs, ["i1", "i2"])

        self.assertIn("output", attributes)
        outputs = attributes["output"]
        self._assert_inclusions(outputs, ["o1", "o2"])

        attributes = get_class_attributes(NoInputsOutputs)
        self.assertEqual(len(attributes), 2)
        inputs = attributes["input"]
        self._assert_inclusions(inputs, ["default"])
        outputs = attributes["output"]
        self._assert_inclusions(outputs, ["default"])

    def test_one_input(self):
        attributes = get_class_attributes(OneInputClass)
        self.assertEqual(len(attributes), 2)

        self.assertIn("input", attributes)
        inputs = attributes["input"]
        self._assert_inclusions(inputs, ["only_input"])

        self.assertIn("output", attributes)
        outputs = attributes["output"]
        self._assert_inclusions(outputs, ["default"])

    def test_one_output(self):
        attributes = get_class_attributes(OneOutputClass)
        self.assertEqual(len(attributes), 2)

        self.assertIn("input", attributes)
        inputs = attributes["input"]
        self._assert_inclusions(inputs, ["default"])

        self.assertIn("output", attributes)
        outputs = attributes["output"]
        self._assert_inclusions(outputs, ["only_output"])

    def _assert_inclusions(self, returned, defined):
        for definition in defined:
            self.assertIn(definition, returned)
        self.assertEqual(len(returned), len(defined))

    def test_user_defaults(self):
        # test class defining 'default' as an input
        inputs = Input.get_class_attribute(UserInputDefaultClass)
        self._assert_inclusions(inputs, ["default", "another_input"])

        attributes = get_class_attributes(UserInputDefaultClass)
        self.assertEqual(len(attributes), 2)

        self.assertIn("input", attributes)
        inputs = attributes["input"]
        self._assert_inclusions(inputs, ["default", "another_input"])

        self.assertIn("output", attributes)
        inputs = attributes["output"]
        self._assert_inclusions(inputs, ["default"])

        # test class defining 'default' as an output
        outputs = Output.get_class_attribute(UserOutputDefaultClass)
        self._assert_inclusions(outputs, ["default", "another_output"])

        attributes = get_class_attributes(UserOutputDefaultClass)
        self.assertEqual(len(attributes), 2)

        self.assertIn("input", attributes)
        inputs = attributes["input"]
        self._assert_inclusions(inputs, ["default"])

        self.assertIn("output", attributes)
        outputs = attributes["output"]
        self._assert_inclusions(outputs, ["default", "another_output"])

        # test class defining 'default' as an input and an output
        inputs = Input.get_class_attribute(UserDefaultsClass)
        self._assert_inclusions(inputs, ["default", "another_input"])

        outputs = Output.get_class_attribute(UserDefaultsClass)
        self._assert_inclusions(outputs, ["default", "another_output"])

        attributes = get_class_attributes(UserDefaultsClass)
        self.assertEqual(len(attributes), 2)

        self.assertIn("input", attributes)
        inputs = attributes["input"]
        self._assert_inclusions(inputs, ["default", "another_input"])

        self.assertIn("output", attributes)
        outputs = attributes["output"]
        self._assert_inclusions(outputs, ["default", "another_output"])
