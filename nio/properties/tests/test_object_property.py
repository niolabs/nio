from nio.signal.base import Signal
from nio.properties import ObjectProperty, PropertyHolder, \
    StringProperty
from nio.util.support.test_case import NIOTestCase


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

    def test_object_property_with_invalid_obj_type(self):
        """Raise TypeError when obj_type is invalid."""
        with self.assertRaisesRegexp(TypeError, 'not a PropertyHolder'):
            class Holder(PropertyHolder):
                property = ObjectProperty(str)
        with self.assertRaisesRegexp(TypeError, 'not a PropertyHolder'):
            class Holder(PropertyHolder):
                property = ObjectProperty('not a property holder')
