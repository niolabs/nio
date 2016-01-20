from enum import Enum
import json
from datetime import timedelta
from nio.block.base import Block
from nio.common.service.base import Service
from nio.metadata.properties import FloatProperty, BoolProperty, SelectProperty
from nio.metadata.properties.int import IntProperty
from nio.metadata.properties.list import ListProperty
from nio.metadata.properties.object import ObjectProperty
from nio.metadata.properties.holder import PropertyHolder
from nio.metadata.properties.string import StringProperty
from nio.util.support.test_case import NIOTestCase
from nio.metadata.properties.timedelta import TimeDeltaProperty


class ContainedClass(PropertyHolder):
    string_property = StringProperty(default="str")
    int_property = IntProperty(default=5)


class SampleEnum(Enum):
    option1 = 0
    option2 = 1
    option3 = 2


class ContainerClass(PropertyHolder):
    string_property = StringProperty(default="string1")
    string_property_default_env_variable = \
        StringProperty(default='[[ENV_VARIABLE]]')

    expression_property = StringProperty(attr_default='Whoops',
                                             default='Default to {{$v1}}')
    expression_property_default_env_variable = \
        StringProperty(default='[[ENV_VARIABLE]]')

    bool_property = BoolProperty(default=False)
    bool_property_default_env_variable = \
        BoolProperty(default='[[ENV_VARIABLE]]')

    int_property = IntProperty(default=8)
    int_property_default_env_variable = IntProperty(default='[[ENV_VARIABLE]]')

    float_property = FloatProperty(default=8.2)
    float_property_default_env_variable = \
        FloatProperty(default='[[ENV_VARIABLE]]')

    object_property = ObjectProperty(ContainedClass)
    object_property_default_env_variable = \
        ObjectProperty(ContainedClass, default='[[ENV_VARIABLE]]')

    list_property1 = ListProperty(ContainedClass, default=[ContainedClass()])
    list_property2 = ListProperty(ContainedClass)
    list_property3 = ListProperty(int, default=[1])
    list_property_default_env_variable = \
        ListProperty(ContainedClass, default='[[ENV_VARIABLE]]')

    timedelta_property = TimeDeltaProperty(default={"seconds": 9})
    timedelta_property_no_default = TimeDeltaProperty()
    timedelta_property_default_env_variable = \
        TimeDeltaProperty(default='[[ENV_VARIABLE]]')

    select_property = SelectProperty(SampleEnum, default=SampleEnum.option2)
    select_property_default_env_variable = \
        SelectProperty(SampleEnum, default='[[ENV_VARIABLE]]')


class MyBlock(Block):
    another_block_property = StringProperty(default="another_block_property")


class TestDefaults(NIOTestCase):

    def test_defaults(self):
        """ Testing that defaults are retrieved and are serializable
        """
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

        self.assertEqual(defaults["object_property"],
                         {'string_property': 'str', 'int_property': 5})
        self.assertEqual(defaults["object_property_default_env_variable"],
                         '[[ENV_VARIABLE]]')

        self.assertEqual(defaults["list_property1"],
                         [{'string_property': 'str', 'int_property': 5}])
        self.assertEqual(defaults["list_property2"], [])
        self.assertEqual(defaults["list_property3"], [1])
        self.assertEqual(defaults["list_property_default_env_variable"],
                         '[[ENV_VARIABLE]]')

        self.assertEqual(defaults["timedelta_property"], timedelta(seconds=9))
        self.assertEqual(defaults["timedelta_property_no_default"],
                         timedelta())
        self.assertEqual(defaults["timedelta_property_default_env_variable"],
                         '[[ENV_VARIABLE]]')

        self.assertEqual(defaults["select_property"], SampleEnum.option2)
        self.assertEqual(defaults["select_property_default_env_variable"],
                         '[[ENV_VARIABLE]]')

        # make sure property description is serializable
        properties_as_str = json.dumps(ContainerClass.get_description())
        self.assertIsNotNone(properties_as_str)

    def test_serializable_defaults(self):
        """ Testing that serializable defaults are different from defaults
        """
        defaults = ContainerClass.get_defaults()
        serializable = ContainerClass.get_serializable_defaults()
        self.assertIsInstance(defaults['timedelta_property'], timedelta)
        self.assertNotIsInstance(serializable['timedelta_property'], timedelta)
        self.assertIsInstance(serializable['timedelta_property'], dict)

    def test_block_defaults(self):
        """ Testing that block defaults are retrieved and are serializable
        """
        defaults = Block.get_defaults()
        defaults2 = MyBlock.get_defaults()
        self.assertNotEqual(defaults, defaults2)
        self.assertEqual(len(defaults) + 1, len(defaults2))
        properties_as_str = json.dumps(defaults)
        self.assertIsNotNone(properties_as_str)

    def test_service_defaults(self):
        """ Testing that service defaults are retrieved and are serializable
        """
        defaults = Service.get_defaults()
        properties_as_str = json.dumps(defaults)
        self.assertIsNotNone(properties_as_str)
