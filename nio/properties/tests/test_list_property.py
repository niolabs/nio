from nio.signal.base import Signal
from nio.properties import IntProperty
from nio.properties import ListProperty
from nio.properties import PropertyHolder
from nio.properties import StringProperty
from nio.types import IntType
from nio.util.support.test_case import NIOTestCaseNoModules


class ContainedClass(PropertyHolder):
    # Note, property name and receiving property have to match
    string_property = StringProperty(default="str")
    int_property = IntProperty(default=5)
    expression_property = StringProperty(default='{{ $value }}')


class ContainerClass(PropertyHolder):
    type_list = ListProperty(IntType, default=[1])
    holder_list = ListProperty(ContainedClass, default=[ContainedClass()])


class TestListProperties(NIOTestCaseNoModules):
    def setUp(self):
        super().setUp()
        # Set up a native object list
        self.type_list_to_use = [1, 2, 3, 4, 5]
        self.invalid_type_list_to_use = ['not an int type']

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

    def test_nio_type_invalid_value(self):
        """Test when a list has a nio Type with invalid values."""
        container = ContainerClass()
        # Set the invalid list
        container.type_list = self.invalid_type_list_to_use
        with self.assertRaises(TypeError):
            container.type_list()

    def test_nio_type(self):
        """Test when a list has a nio Type."""

        container = ContainerClass()

        # Set the list
        container.type_list = self.type_list_to_use

        # Now make sure getting the list gets the same one
        self.assertEqual(self.type_list_to_use, container.type_list())

    def test_holder_type(self):
        """Test when a list has is a PropertyHolder type."""

        container = ContainerClass()

        # Set the list
        container.holder_list = self.holder_list_to_use

        # Now make sure getting the list gets the same one
        self.assertEqual(self.holder_list_to_use, container.holder_list())

    def test_to_from_dict(self):
        """Make sure the serialize/deserialze hold."""

        container_1 = ContainerClass()
        container_1.type_list = self.type_list_to_use
        container_1.holder_list = self.holder_list_to_use

        # Load container 2 with the dictionary of container 1
        container_2 = ContainerClass()
        one = container_1.to_dict()
        container_2.from_dict(one)
        two = container_2.to_dict()

        self.assertEqual(one, two)

    def test_bad_dict(self):
        """Raise TypeError when deserializing non-list items."""

        invalid_props = {
            "type_list": "not a list"
        }
        container_1 = ContainerClass()
        # You can set invalid props
        container_1.from_dict(invalid_props)
        with self.assertRaises(TypeError):
            # But deserializing in validate_dict is not ok
            container_1.validate_dict(invalid_props)

    def test_expression(self):
        """Test expressions for list property."""
        container = ContainerClass()
        contained = ContainedClass()
        contained.expression_property = "three is {{ 1 + 2 }}"
        container.holder_list = [contained]
        self.assertIsNotNone(container.holder_list)
        self.assertEqual(
            container.holder_list()[0].expression_property(), 'three is 3')

    def test_expression_with_signal(self):
        """Test signal expressions for list property."""
        container = ContainerClass()
        contained = ContainedClass()
        self.assertIsNotNone(container.holder_list)
        self.assertEqual(container.holder_list()[0].
                         expression_property(Signal({'value': 'signal'})),
                         'signal')

    def test_defaults(self):
        """Test list defaults."""
        defaults = ContainerClass.get_serializable_defaults()
        self.assertEqual(defaults["type_list"], [1])
        self.assertEqual(defaults["holder_list"],
                         [{'string_property': 'str',
                           'int_property': 5,
                           'expression_property' : '{{ $value }}'}])
