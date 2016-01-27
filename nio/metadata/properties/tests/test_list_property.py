from nio.common.signal.base import Signal
from nio.metadata.properties.int import IntProperty
from nio.metadata.properties.list import ListProperty
from nio.metadata.properties.holder import PropertyHolder
from nio.metadata.properties.string import StringProperty
from nio.util.support.test_case import NIOTestCase


class ContainedClass(PropertyHolder):
    # Note, property name and receiving property have to match
    string_property = StringProperty(default="str")
    int_property = IntProperty(default=5)
    expression_property = StringProperty(default='{{ $value }}')


class ContainerClass(PropertyHolder):
    native_list = ListProperty(int)
    holder_list = ListProperty(ContainedClass, default=[ContainedClass()])
    property_list = ListProperty(IntProperty)


class TestListProperties(NIOTestCase):
    def setUp(self):
        super().setUp()
        # Set up a native object list
        self.native_list_to_use = [1, 2, 3, 4, 5]

        # Set up a holder object list
        contained_a = ContainedClass()
        contained_a.string_property = "test_a"
        contained_a.int_property = 1
        contained_a.expression_property = 'expression_a'

        contained_b = ContainedClass()
        contained_b.string_property = "test_b"
        contained_b.int_property = 2
        contained_b.expression_property = 'expression_b'

        self.holder_list_to_use = [contained_a, contained_b, ContainedClass()]

        # Set up a property object list
        prop_a = IntProperty(default=1)
        prop_b = IntProperty(default=2)

        self.prop_list_to_use = [prop_a, prop_b, IntProperty(default=3)]

    def test_native_type(self):
        """Test when a list has a native python type"""

        container = ContainerClass()

        # Set the list
        container.native_list = self.native_list_to_use

        # Now make sure getting the list gets the same one
        self.assertEqual(self.native_list_to_use, container.native_list())

    def test_holder_type(self):
        """Test when a list has a native python type"""

        container = ContainerClass()

        # Set the list
        container.holder_list = self.holder_list_to_use

        # Now make sure getting the list gets the same one
        self.assertEqual(self.holder_list_to_use, container.holder_list())

    def test_property_type(self):
        """Test when a list has a native python type"""

        container = ContainerClass()

        # Set the list
        container.property_list = self.prop_list_to_use

        # Now make sure getting the list gets the same one
        self.assertEqual(self.prop_list_to_use, container.property_list())

    def test_to_from_dict(self):
        """Make sure the serialize/deserialze hold"""

        container_1 = ContainerClass()
        container_1.native_list = self.native_list_to_use
        container_1.holder_list = self.holder_list_to_use
        container_1.property_list = self.prop_list_to_use

        container_2 = ContainerClass()
        # Load container 2 with the dictionary of container 1
        one = container_1.to_dict()
        container_2.from_dict(one)

        self.assertEqual(container_1.to_dict(), container_2.to_dict())

    def test_bad_dict(self):
        """Make sure attempts to deserialize something not a list
        raises a TypeError"""

        invalid_props = {
            "native_list": "not a list"
        }
        container_1 = ContainerClass()

        self.assertRaises(TypeError, container_1.from_dict, invalid_props)

    def test_expression(self):
        container = ContainerClass()
        contained = ContainedClass()
        contained.expression_property = "three is {{ 1 + 2 }}"
        container.holder_list = [contained]
        self.assertIsNotNone(container.holder_list)
        self.assertEqual(
            container.holder_list()[0].expression_property(), 'three is 3')

    def test_expression_with_signal(self):
        container = ContainerClass()
        contained = ContainedClass()
        self.assertIsNotNone(container.holder_list)
        self.assertEqual(container.holder_list()[0].
                         expression_property(Signal({'value': 'signal'})),
                         'signal')
