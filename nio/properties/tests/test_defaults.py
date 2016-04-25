import json
from datetime import timedelta
from enum import Enum

from nio.block.base import Block
from nio.service.base import Service
from nio.properties import FloatProperty, BoolProperty, SelectProperty
from nio.properties import IntProperty
from nio.properties import ListProperty
from nio.properties import ObjectProperty
from nio.properties import PropertyHolder
from nio.properties import StringProperty
from nio.properties import TimeDeltaProperty
from nio.types import IntType
from nio.testing.test_case import NIOTestCaseNoModules


class ContainedClass(PropertyHolder):
    string_property = StringProperty("string_property", default="str")
    int_property = IntProperty("int_property", default=5)


class SampleEnum(Enum):
    option1 = 0
    option2 = 1
    option3 = 2


class ContainerClass(PropertyHolder):
    string_property = StringProperty("string_property", default="string1")
    string_property_default_env_variable = \
        StringProperty("string_property_default_env_variable",
                       default='[[ENV_VARIABLE]]')

    expression_property = \
        StringProperty("expression_property", default='Default to {{$v1}}')
    expression_property_default_env_variable = \
        StringProperty("expression_property_default_env_variable",
                       default='[[ENV_VARIABLE]]')

    bool_property = BoolProperty("bool_property", default=False)
    bool_property_default_env_variable = \
        BoolProperty("bool_property_default_env_variable",
                     default='[[ENV_VARIABLE]]')

    int_property = IntProperty("int_property", default=8)
    int_property_default_env_variable = \
        IntProperty("int_property_default_env_variable",
                    default='[[ENV_VARIABLE]]')

    float_property = FloatProperty("float_property", default=8.2)
    float_property_default_env_variable = \
        FloatProperty("float_property_default_env_variable",
                      default='[[ENV_VARIABLE]]')

    object_property = \
        ObjectProperty("object_property", ContainedClass,
                       default=ContainedClass())
    object_property_default_env_variable = \
        ObjectProperty("object_property_default_env_variable", ContainedClass,
                       default='[[ENV_VARIABLE]]')

    list_property1 = \
        ListProperty("list_property1", ContainedClass,
                     default=[ContainedClass()])
    list_property2 = ListProperty("list_property2", ContainedClass)
    list_property3 = ListProperty("list_property3", IntType, default=[1])
    list_property_default_env_variable = \
        ListProperty("list_property_default_env_variable", ContainedClass,
                     default='[[ENV_VARIABLE]]')

    timedelta_property = TimeDeltaProperty("timedelta_property",
                                           default={"seconds": 9})
    timedelta_property_no_default = \
        TimeDeltaProperty("timedelta_property_no_default")
    timedelta_property_default_env_variable = \
        TimeDeltaProperty("timedelta_property_default_env_variable",
                          default='[[ENV_VARIABLE]]')

    select_property = \
        SelectProperty("select_property", SampleEnum,
                       default=SampleEnum.option2)
    select_property_default_env_variable = \
        SelectProperty("select_property_default_env_variable", SampleEnum,
                       default='[[ENV_VARIABLE]]')


class MyBlock(Block):
    another_block_property = \
        StringProperty("another_block_property",
                       default="another_block_property")


class TestDefaults(NIOTestCaseNoModules):

    def test_defaults(self):
        """Testing that defaults are retrieved"""
        defaults = ContainerClass.get_defaults()
        defaults2 = ContainerClass.get_defaults()
        # assert that obtaining it twice doesn't change anything
        self.assertEqual(defaults, defaults2)

        self.assertEqual(defaults["string_property"], "string1")
        self.assertEqual(defaults["string_property_default_env_variable"],
                         '[[ENV_VARIABLE]]')

        self.assertEqual(defaults["expression_property"], 'Default to {{$v1}}')
        self.assertEqual(defaults["string_property_default_env_variable"],
                         '[[ENV_VARIABLE]]')

        self.assertEqual(defaults["int_property"], 8)
        self.assertEqual(defaults["int_property_default_env_variable"],
                         '[[ENV_VARIABLE]]')

        self.assertEqual(defaults["float_property"], 8.2)
        self.assertEqual(defaults["float_property_default_env_variable"],
                         '[[ENV_VARIABLE]]')

        self.assertEqual(defaults["object_property"].string_property(),
                         'str')
        self.assertEqual(defaults["object_property"].int_property(),
                         5)
        self.assertEqual(defaults["object_property_default_env_variable"],
                         '[[ENV_VARIABLE]]')

        self.assertEqual(defaults["list_property1"][0].string_property(),
                         'str')
        self.assertEqual(defaults["list_property1"][0].int_property(),
                         5)
        self.assertEqual(defaults["list_property2"], None)
        self.assertEqual(defaults["list_property3"], [1])
        self.assertEqual(defaults["list_property_default_env_variable"],
                         '[[ENV_VARIABLE]]')

        self.assertEqual(defaults["timedelta_property"], timedelta(seconds=9))
        self.assertEqual(defaults["timedelta_property_no_default"],
                         None)
        self.assertEqual(defaults["timedelta_property_default_env_variable"],
                         '[[ENV_VARIABLE]]')

        self.assertEqual(defaults["select_property"], SampleEnum.option2)
        self.assertEqual(defaults["select_property_default_env_variable"],
                         '[[ENV_VARIABLE]]')

        # make sure property description is serializable
        properties_as_str = json.dumps(ContainerClass.get_description())
        self.assertIsNotNone(properties_as_str)

    def test_serializable_defaults(self):
        """Testing that serializable defaults are different from defaults."""
        defaults = ContainerClass.get_defaults()
        serializable = ContainerClass.get_serializable_defaults()
        # Test timedelta property
        self.assertIsInstance(defaults['timedelta_property'], timedelta)
        self.assertNotIsInstance(serializable['timedelta_property'], timedelta)
        self.assertIsInstance(serializable['timedelta_property'], dict)
        # Test object property
        self.assertIsInstance(defaults['object_property'], ContainedClass)
        self.assertIsInstance(serializable['object_property'], dict)
        self.assertDictEqual(serializable["object_property"],
                             {'string_property': 'str', 'int_property': 5})
        # Test list property of objects
        self.assertIsInstance(defaults['list_property1'], list)
        self.assertIsInstance(defaults['list_property1'][0], ContainedClass)
        self.assertIsInstance(serializable['list_property1'], list)
        self.assertIsInstance(serializable['list_property1'][0], dict)
        self.assertEqual(len(serializable['list_property1']), 1)
        self.assertDictEqual(serializable["list_property1"][0],
                             {'string_property': 'str', 'int_property': 5})

    def test_block_defaults(self):
        """Testing that block defaults are retrieved and are serializable."""
        defaults = Block.get_serializable_defaults()
        defaults2 = MyBlock.get_serializable_defaults()
        self.assertNotEqual(defaults, defaults2)
        self.assertEqual(len(defaults) + 1, len(defaults2))
        properties_as_str = json.dumps(defaults)
        self.assertIsNotNone(properties_as_str)

    def test_service_defaults(self):
        """Testing that service defaults are retrieved and are serializable."""
        defaults = Service.get_serializable_defaults()
        properties_as_str = json.dumps(defaults)
        self.assertIsNotNone(properties_as_str)
