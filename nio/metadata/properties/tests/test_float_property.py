from nio.util.support.test_case import NIOTestCase
from nio.metadata.properties import FloatProperty, PropertyHolder
from nio.common.signal.base import Signal


class ContainerClass(PropertyHolder):
    property = FloatProperty()
    default = FloatProperty(default=1.23)


class TestFloatProperty(NIOTestCase):

    def test_default(self):
        container = ContainerClass()
        self.assertIsNotNone(container.property)
        self.assertEqual(container.property(), 0)
        self.assertEqual(container.default.default, 1.23)

    def test_expression(self):
        container = ContainerClass()
        container.property = "{{ 1 + 2.1 }}"
        self.assertIsNotNone(container.property)
        self.assertEqual(container.property(), 3.1)
        self.assertEqual(container.default.default, 1.23)

    def test_expression_with_signal(self):
        container = ContainerClass()
        container.property = "{{ $value }}"
        self.assertIsNotNone(container.property)
        self.assertEqual(container.property(Signal({'value': 42.1})), 42.1)
