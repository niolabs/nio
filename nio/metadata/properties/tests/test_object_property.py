from nio.util.support.test_case import NIOTestCase
from nio.metadata.properties import ObjectProperty, PropertyHolder, \
    StringProperty
from nio.common.signal.base import Signal


class ContainedClass(PropertyHolder):
    sub_property = StringProperty(default='')


class ContainerClass(PropertyHolder):
    property = ObjectProperty(ContainedClass, default=ContainedClass())


class TestObjectProperty(NIOTestCase):

    def test_default(self):
        container = ContainerClass()
        self.assertIsNotNone(container.property)
        self.assertEqual(type(container.property()), ContainedClass)

    def test_expression(self):
        container = ContainerClass()
        contained = ContainedClass()
        contained.sub_property = "three is {{ 1 + 2 }}"
        container.property = contained
        self.assertIsNotNone(container.property)
        self.assertEqual(container.property().sub_property(), 'three is 3')

    def test_expression_with_signal(self):
        container = ContainerClass()
        contained = ContainedClass()
        contained.sub_property = "{{ $value }}"
        container.property = contained
        self.assertIsNotNone(container.property)
        self.assertEqual(container.property().sub_property(
            Signal({'value': 'sub-meta'})), 'sub-meta')
