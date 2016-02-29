import json
from enum import Enum

from nio.properties import PropertyHolder
from nio.properties import SelectProperty
from nio.util.support.test_case import NIOTestCaseNoModules


class SampleEnum(Enum):
    option1 = 0
    option2 = 1
    option3 = 2


class SampleClass(PropertyHolder):

    # Note, property name and receiving property have to match
    select_property = \
        SelectProperty(SampleEnum, default=SampleEnum.option3)


class TestProperties(NIOTestCaseNoModules):

    def test_description(self):
        """Description contains select property options."""
        description = SampleClass.get_description()
        descr_json = json.dumps(description)
        self.assertIsInstance(json.loads(descr_json), dict)
        self.assertIn('select_property', description)
        prop = description.get('select_property')
        self.assertIsNotNone(prop.get('options'))
        self.assertIn('options', prop)
        prop_opt = prop.get('options')
        self.assertDictEqual(prop_opt, {
            'option1': 0,
            'option2': 1,
            'option3': 2
        })

    def test_deserialize(self):
        """Test select property deserialize works with various defaults."""
        prop = SelectProperty(SampleEnum, default=SampleEnum.option1)
        self.assertEqual(prop.deserialize(prop.default), SampleEnum.option1)
        prop = SelectProperty(SampleEnum, default='option1')
        self.assertEqual(prop.deserialize(prop.default), SampleEnum.option1)
        prop = SelectProperty(SampleEnum, default=0)
        self.assertEqual(prop.deserialize(prop.default), SampleEnum.option1)
        prop = SelectProperty(SampleEnum, default=SampleEnum.option1.value)
        self.assertEqual(prop.deserialize(prop.default), SampleEnum.option1)

        prop = SelectProperty(SampleEnum)
        with self.assertRaises(TypeError):
            prop.deserialize('foo')
