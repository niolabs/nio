from nio.signal.base import Signal
from nio.properties import IntProperty, PropertyHolder
from nio.testing.test_case import NIOTestCaseNoModules


class ContainerClass(PropertyHolder):
    property = IntProperty()
    default = IntProperty(default=1)


class TestIntProperty(NIOTestCaseNoModules):

    def test_default(self):
        """Test default behavior of int property."""
        container = ContainerClass()
        self.assertIsNotNone(container.property)
        with self.assertRaises(Exception):
            container.property()
        self.assertEqual(container.default(), 1)
        self.assertEqual(container.default._property.default, 1)

    def test_expression(self):
        """Test expressions for int property."""
        container = ContainerClass()
        container.property = "{{ 1 + 2 }}"
        self.assertIsNotNone(container.property)
        self.assertEqual(container.property(), 3)
        self.assertEqual(container.default._property.default, 1)

    def test_expression_with_signal(self):
        """Test signal expressions for int property."""
        container = ContainerClass()
        container.property = "{{ $value }}"
        self.assertIsNotNone(container.property)
        self.assertEqual(container.property(Signal({'value': 42.1})), 42)
