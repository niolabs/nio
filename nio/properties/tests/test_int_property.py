from nio.common.signal.base import Signal
from nio.properties import IntProperty, PropertyHolder
from nio.util.support.test_case import NIOTestCase


class ContainerClass(PropertyHolder):
    property = IntProperty()
    default = IntProperty(default=1)


class TestIntProperty(NIOTestCase):

    def test_default(self):
        container = ContainerClass()
        self.assertIsNotNone(container.property)
        with self.assertRaises(Exception):
            container.property()
        self.assertEqual(container.default(), 1)
        # TODO: add ability to get 'default' from PropertyValue
        #self.assertEqual(container.default.default, 1)

    def test_expression(self):
        container = ContainerClass()
        container.property = "{{ 1 + 2 }}"
        self.assertIsNotNone(container.property)
        self.assertEqual(container.property(), 3)
        #self.assertEqual(container.default.default, 1)

    def test_expression_with_signal(self):
        container = ContainerClass()
        container.property = "{{ $value }}"
        self.assertIsNotNone(container.property)
        self.assertEqual(container.property(Signal({'value': 42.1})), 42)
