from unittest.mock import MagicMock
from nio.properties.exceptions import AllowNoneViolation
from nio.properties.base import BaseProperty
from nio.properties.holder import PropertyHolder
from nio.properties.util.property_value import PropertyValue
from nio.signal.base import Signal
from nio.types.base import Type
from nio.util.support.test_case import NIOTestCase


class SampleHolder(PropertyHolder):
    pass


class TestPropertyValue(NIOTestCase):

    def test_expression(self):
        property = BaseProperty(Type)
        property_value = PropertyValue(property, value="{{ 'value' }}")
        value = property_value()
        self.assertEqual(value, 'value')

    def test_expression_with_signal(self):
        property = BaseProperty(Type)
        property_value = PropertyValue(property, value="{{ $attr }}")
        value = property_value(Signal({"attr": "value"}))
        self.assertEqual(value, 'value')

    def test_allow_none_is_false(self):
        property = BaseProperty(Type)
        property_value = PropertyValue(property, value=None)
        with self.assertRaises(AllowNoneViolation):
            value = property_value()

    def test_allow_none_is_true(self):
        property = BaseProperty(Type, allow_none=True)
        property_value = PropertyValue(property, value=None)
        value = property_value()
        self.assertEqual(value, None)

    def test_allow_none_is_false_with_expression(self):
        property = BaseProperty(Type)
        property_value = PropertyValue(property, value="{{ None }}")
        with self.assertRaises(AllowNoneViolation):
            value = property_value()

    def test_allow_none_is_true_with_expression(self):
        property = BaseProperty(Type, allow_none=True)
        property_value = PropertyValue(property, value="{{ None }}")
        value = property_value()
        self.assertEqual(value, None)

    def test_property_holder(self):
        property = BaseProperty(Type)
        property_holder = SampleHolder()
        property_value = PropertyValue(property, value=property_holder)
        value = property_value()
        self.assertEqual(value, property_holder)
