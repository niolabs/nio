from nio.util.support.test_case import NIOTestCase
from nio.metadata.properties import FloatProperty, PropertyHolder
from nio.common.signal.base import Signal


class ContainerClass(PropertyHolder):
    property = FloatProperty()


class TestIntProperty(NIOTestCase):

    def test_attr_default(self):
        container = ContainerClass()
        self.assertIsNotNone(container.property)
        self.assertEqual(container.property(), 0)

    def test_expression(self):
        container = ContainerClass()
        container.property = "{{ 1 + 2 }}"
        self.assertIsNotNone(container.property)
        self.assertEqual(container.property(), 3)

    def test_expression_with_signal(self):
        container = ContainerClass()
        container.property = "{{ $value }}"
        self.assertIsNotNone(container.property)
        self.assertEqual(container.property(Signal({'value': 42.1})), 42.1)
