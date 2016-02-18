from nio.properties import PropertyHolder
from nio.properties import VarProperty
from nio.util.support.test_case import NIOTestCase


class SampleClass(PropertyHolder):
    var_property = VarProperty(allow_none=True)


class TestVarProperty(NIOTestCase):

    def test_initialization(self):
        """ Make sure we can initialize and have the property """
        instance = SampleClass()
        self.assertIsNotNone(instance.var_property)
        self.assertIsNone(instance.var_property())

    def test_accept_anything(self):
        """ The property should accept anything """
        instance = SampleClass()

        # Anything includes an integer
        instance.var_property = 5
        self.assertEqual(instance.var_property(), 5)

        # Anything includes a string
        instance.var_property = "string"
        self.assertEqual(instance.var_property(), "string")

        # Anything includes a list
        instance.var_property = []
        self.assertEqual(instance.var_property(), [])

    def test_serialize_deserialize_matching(self):
        """Serialize then deserialize should match the original"""
        instance1 = SampleClass()
        instance1.var_property = []
        instance1_serialized = instance1.to_dict()

        # set up instance 2 from instance1 serialization
        instance2 = SampleClass()
        instance2.from_dict(instance1_serialized)
        instance2_serialized = instance2.to_dict()
        self.assertDictEqual(instance2_serialized, instance1_serialized)

    def test_deserialize_serialize_matching(self):
        """Deserialize then serialize should match the original"""
        my_dict = {
            'var_property': []
        }
        instance1 = SampleClass()
        instance1.from_dict(my_dict)
        self.assertEqual(instance1.var_property(), [])
        self.assertDictEqual(instance1.to_dict(), my_dict)
