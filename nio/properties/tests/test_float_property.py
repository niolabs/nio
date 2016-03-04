from nio.signal.base import Signal
from nio.properties import FloatProperty, PropertyHolder
from nio.testing.test_case import NIOTestCaseNoModules


class ContainerClass(PropertyHolder):
    property = FloatProperty()
    default = FloatProperty(default=1.23)


class TestFloatProperty(NIOTestCaseNoModules):

    def test_default(self):
        """Test default behavior of float property."""
        container = ContainerClass()
        self.assertIsNotNone(container.property)
        self.assertEqual(container.default(), 1.23)
        self.assertEqual(container.default._property.default, 1.23)

    def test_expression(self):
        """Test expressions for float property."""
        container = ContainerClass()
        container.property = "{{ 1 + 2.1 }}"
        self.assertIsNotNone(container.property)
        self.assertEqual(container.property(), 3.1)
        self.assertEqual(container.default._property.default, 1.23)

    def test_expression_with_signal(self):
        """Test signal expressions for float property."""
        container = ContainerClass()
        container.property = "{{ $value }}"
        self.assertIsNotNone(container.property)
        self.assertEqual(container.property(Signal({'value': 42.1})), 42.1)
