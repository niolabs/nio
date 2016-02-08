import json
from enum import Enum

from nio.properties import PropertyHolder
from nio.properties import SelectProperty
from nio.util.support.block_test_case import NIOBlockTestCase


class SampleEnum(Enum):
    option1 = 0
    option2 = 1
    option3 = 2


class SampleClass(PropertyHolder):

    # Note, property name and receiving property have to match
    select_property = \
        SelectProperty(SampleEnum, default=SampleEnum.option3)


class TestProperties(NIOBlockTestCase):

    def test_initialization(self):
        instance = SampleClass()
        # make sure definitions are in the class
        self.assertIsNotNone(instance.select_property)

    def test_accept_values(self):
        instance = SampleClass()

        self.assertEqual(instance.select_property(), SampleEnum.option3)

        # assert that it takes values
        instance.select_property = SampleEnum.option2

        # assert that the values matched when reading them
        self.assertEqual(instance.select_property(), SampleEnum.option2)

    def test_serialize_deserialize_matching(self):

        properties_to_set = {"select_property": SampleEnum.option3}
        properties_serialized = {"select_property": SampleEnum.option3.name}

        # matching assignments with properties_to_set
        instance = SampleClass()
        instance.select_property = properties_to_set['select_property']

        # the serialized container should match properties_to_set
        instance_serialized = instance.to_dict()
        self.assertEqual(instance_serialized, properties_serialized)

        instance2 = SampleClass()
        # assign from dictionary
        instance2.from_dict(properties_serialized)
        instance2_serialized = instance2.to_dict()
        self.assertEqual(instance_serialized, instance2_serialized)

    def test_description(self):
        """ access description from class """
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
