from enum import Enum

from nio.properties import FloatProperty, SelectProperty, \
    BoolProperty
from nio.properties import IntProperty
from nio.properties import ListProperty
from nio.properties import ObjectProperty
from nio.properties import PropertyHolder
from nio.properties import StringProperty
from nio.properties import TimeDeltaProperty
from nio.types import BoolType
from nio.types import FloatType
from nio.types import IntType
from nio.types import ListType
from nio.types import ObjectType
from nio.types import SelectType
from nio.types import StringType
from nio.types import TimeDeltaType
from nio.util.support.test_case import NIOTestCase


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

    expression_property = StringProperty(default='Default to {{$v1}}')
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

    select_property = SelectProperty(
        SampleEnum, default=SampleEnum.option2)
    select_property_default_env_variable = \
        SelectProperty(SampleEnum, default='[[ENV_VARIABLE]]')


class TestTypes(NIOTestCase):
    def test_types(self):
        """ Testing that defaults are retrieved and are serializable
        """
        description = ContainerClass.get_description()

        self.assertEqual(description['string_property']['type'],
                         StringType.__name__)
        self.assertEqual(description['string_property_default_env_variable']
                         ['type'], StringType.__name__)

        self.assertEqual(description['expression_property']['type'],
                         StringType.__name__)
        self.assertEqual(
            description['expression_property_default_env_variable']
            ['type'], StringType.__name__)

        self.assertEqual(description['bool_property']['type'],
                         BoolType.__name__)
        self.assertEqual(description['bool_property_default_env_variable']
                         ['type'], BoolType.__name__)

        self.assertEqual(description['int_property']['type'],
                         IntType.__name__)
        self.assertEqual(description['int_property_default_env_variable']
                         ['type'], IntType.__name__)

        self.assertEqual(description['float_property']['type'],
                         FloatType.__name__)
        self.assertEqual(description['float_property_default_env_variable']
                         ['type'], FloatType.__name__)

        self.assertEqual(description['object_property']['type'],
                         ObjectType.__name__)
        self.assertEqual(description['object_property_default_env_variable']
                         ['type'], ObjectType.__name__)

        self.assertEqual(description['list_property1']['type'],
                         ListType.__name__)
        self.assertEqual(description['list_property2']['type'],
                         ListType.__name__)
        self.assertEqual(description['list_property3']['type'],
                         ListType.__name__)
        self.assertEqual(description['list_property_default_env_variable']
                         ['type'], ListType.__name__)

        self.assertEqual(description['timedelta_property']['type'],
                         TimeDeltaType.__name__)
        self.assertEqual(description['timedelta_property_no_default']['type'],
                         TimeDeltaType.__name__)

        self.assertEqual(description['select_property']['type'],
                         SelectType.__name__)
        self.assertEqual(description['select_property_default_env_variable']
                         ['type'], SelectType.__name__)
