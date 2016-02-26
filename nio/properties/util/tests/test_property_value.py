from unittest.mock import MagicMock
from nio.properties.exceptions import AllowNoneViolation
from nio.properties.base import BaseProperty
from nio.properties.holder import PropertyHolder
from nio.properties.util.property_value import PropertyValue
from nio.signal.base import Signal
from nio.types.base import Type
from nio.util.support.test_case import NIOTestCaseNoModules


class SampleHolder(PropertyHolder):
    pass


class TestPropertyValue(NIOTestCaseNoModules):

    def test_expression(self):
        """PropertyValues support expressions."""
        property = BaseProperty(Type)
        property_value = PropertyValue(property, value="{{ 'value' }}")
        value = property_value()
        self.assertEqual(value, 'value')

    def test_expression_with_signal(self):
        """PropertyValues support expressions with signals."""
        property = BaseProperty(Type)
        property_value = PropertyValue(property, value="{{ $attr }}")
        value = property_value(Signal({"attr": "value"}))
        self.assertEqual(value, 'value')

    def test_allow_none_is_false(self):
        """AllowNoneViolation if allow_none is violated."""
        property = BaseProperty(Type)
        property_value = PropertyValue(property, value=None)
        with self.assertRaises(AllowNoneViolation):
            value = property_value()

    def test_allow_none_is_true(self):
        """None is allowed if allow_none is True."""
        property = BaseProperty(Type, allow_none=True)
        property_value = PropertyValue(property, value=None)
        value = property_value()
        self.assertEqual(value, None)

    def test_allow_none_is_false_with_expression(self):
        """AllowNoneViolation if allow_none is violated by expression."""
        property = BaseProperty(Type)
        property_value = PropertyValue(property, value="{{ None }}")
        with self.assertRaises(AllowNoneViolation):
            value = property_value()

    def test_allow_none_is_true_with_expression(self):
        """Expressions can evaluate to None if allow_none is True."""
        property = BaseProperty(Type, allow_none=True)
        property_value = PropertyValue(property, value="{{ None }}")
        value = property_value()
        self.assertEqual(value, None)

    def test_property_holder(self):
        """PropertyValue values can be PropertyHolders."""
        property = BaseProperty(Type)
        property_holder = SampleHolder()
        property_value = PropertyValue(property, value=property_holder)
        value = property_value()
        self.assertEqual(value, property_holder)
