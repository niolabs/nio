from enum import Enum
from datetime import timedelta
from nio.metadata.properties import FloatProperty, SelectProperty, \
    BoolProperty, StringProperty
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

    float_property = FloatProperty(default=8)
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

    select_property = SelectProperty(SampleEnum, default=SampleEnum.option2)
    select_property_default_env_variable = \
        SelectProperty(SampleEnum, default='[[ENV_VARIABLE]]')


class TestTypes(NIOTestCase):
    def test_types(self):
        """ Testing that defaults are retrieved and are serializable
        """
        description = ContainerClass.get_description()

        self.assertEqual(description['string_property']['type'],
                         str.__name__)
        self.assertEqual(description['string_property_default_env_variable']
                         ['type'], str.__name__)

        self.assertEqual(description['expression_property']['type'],
                         "str")
        self.assertEqual(
            description['expression_property_default_env_variable']
            ['type'], "str")

        self.assertEqual(description['bool_property']['type'],
                         bool.__name__)
        self.assertEqual(description['bool_property_default_env_variable']
                         ['type'], bool.__name__)

        self.assertEqual(description['int_property']['type'],
                         int.__name__)
        self.assertEqual(description['int_property_default_env_variable']
                         ['type'], int.__name__)

        self.assertEqual(description['float_property']['type'],
                         float.__name__)
        self.assertEqual(description['float_property_default_env_variable']
                         ['type'], float.__name__)

        self.assertEqual(description['object_property']['type'],
                         object.__name__)
        self.assertEqual(description['object_property_default_env_variable']
                         ['type'], object.__name__)

        self.assertEqual(description['list_property1']['type'],
                         list.__name__)
        self.assertEqual(description['list_property2']['type'],
                         list.__name__)
        self.assertEqual(description['list_property3']['type'],
                         list.__name__)
        self.assertEqual(description['list_property_default_env_variable']
                         ['type'], list.__name__)

        self.assertEqual(description['timedelta_property']['type'],
                         timedelta.__name__)
        self.assertEqual(description['timedelta_property_no_default']['type'],
                         timedelta.__name__)

        self.assertEqual(description['select_property']['type'],
                         "select")
        self.assertEqual(description['select_property_default_env_variable']
                         ['type'], "select")
