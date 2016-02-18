from unittest.mock import MagicMock, patch

from nio.properties import BaseProperty
from nio.properties.util.property_value import PropertyValue
from nio.types import Type
from nio.util.support.test_case import NIOTestCase


class TestBaseProperty(NIOTestCase):

    def test_set(self):
        """ Set a value and store a PropertyValue in Base._values """
        mocked_instance = MagicMock()
        property = BaseProperty(Type)
        # Initially, _values is empty
        self.assertEqual(len(property._values), 0)
        set_values = ["", "string", 1, {}, []]
        for set_value in set_values:
            property.__set__(mocked_instance, set_value)
            self.assertEqual(len(property._values), 1)
            self.assertIsInstance(
                property._values[mocked_instance], PropertyValue)
            self.assertEqual(
                property._values[mocked_instance].value, set_value)

    def test_get(self):
        """ Get the PropertyValue from Base._values for the given instance """
        mocked_instance = MagicMock()
        mocked_property_value = MagicMock(spec=PropertyValue)
        property = BaseProperty(Type)
        # Pre-populate _values with a value for this instance
        property._values[mocked_instance] = mocked_property_value
        self.assertEqual(len(property._values), 1)
        # The property value is the mocked one that was set
        property_value = property.__get__(mocked_instance, MagicMock())
        self.assertEqual(len(property._values), 1)
        self.assertIsInstance(property._values[mocked_instance], PropertyValue)
        self.assertEqual(property_value, mocked_property_value)

    def test_get_default(self):
        """ Get the default PropertyValue when a value is not yet set """
        mocked_instance = MagicMock()
        default_value = MagicMock()
        property = BaseProperty(Type, default=default_value)
        self.assertEqual(len(property._values), 0)
        # The property value's value is the property default value
        property_value = property.__get__(mocked_instance, MagicMock())
        self.assertEqual(len(property._values), 0)
        self.assertIsInstance(property_value, PropertyValue)
        self.assertEqual(property_value.value, default_value)

    def test_set_and_get_value(self):
        """ Test the whole set, get, and call process """
        mocked_instance = MagicMock()
        property = BaseProperty(Type)
        set_values = ["", "string", 1, {}, []]
        get_values = []
        for set_value in set_values:
            property.__set__(mocked_instance, set_value)
            property_value = property.__get__(mocked_instance, MagicMock())
            value = property_value()
            get_values.append(value)
        self.assertEqual(set_values, get_values)

    def test_allow_none_is_false(self):
        """ None is allowed to be set but raises an exception when used """
        mocked_instance = MagicMock()
        property = BaseProperty(Type, allow_none=False)
        set_value = None
        property.__set__(mocked_instance, set_value)
        property_value = property.__get__(mocked_instance, MagicMock())
        with self.assertRaises(Exception):
            value = property_value()

    def test_allow_none_is_true(self):
        """ None values are alowed when allow_none is True """
        mocked_instance = MagicMock()
        property = BaseProperty(Type, allow_none=True)
        set_value = None
        property.__set__(mocked_instance, set_value)
        property_value = property.__get__(mocked_instance, MagicMock())
        value = property_value()
        self.assertEqual(set_value, value)

    def test_serialize_with_normal_value(self):
        """ Call Type.serialize and return the serialized value """
        mocked_serialized_value = MagicMock()
        mocked_instance = MagicMock()
        property = BaseProperty(Type)
        property.is_expression = MagicMock(return_value=False)
        property.is_env_var = MagicMock(return_value=False)
        property._values[mocked_instance] = MagicMock()
        with patch('nio.types.Type.serialize',
                   return_value=mocked_serialized_value):
            serialized_value = property.serialize(mocked_instance)
        self.assertEqual(serialized_value, mocked_serialized_value)

    def test_serialize_with_default_value(self):
        """ Return the raw default value if a value is not yet set """
        mocked_instance = MagicMock()
        default_value = MagicMock()
        property = BaseProperty(Type, default=default_value)
        property.is_expression = MagicMock(return_value=False)
        property.is_env_var = MagicMock(return_value=False)
        serialized_value = property.serialize(mocked_instance)
        self.assertEqual(serialized_value, default_value)

    def test_serialize_with_expression_value(self):
        """ Return raw PropertyValue.value if it's an expression """
        mocked_serialized_value = MagicMock()
        mocked_instance = MagicMock()
        property = BaseProperty(Type)
        property.is_expression = MagicMock(return_value=True)
        property.is_env_var = MagicMock(return_value=False)
        mocked_property_value = MagicMock()
        property._values[mocked_instance] = mocked_property_value
        with patch('nio.types.Type.serialize',
                   return_value=mocked_serialized_value):
            serialized_value = property.serialize(mocked_instance)
        self.assertEqual(serialized_value, mocked_property_value.value)

    def test_serialize_with_env_var_value(self):
        """ Return raw PropertyValue.value if it's an environment variable """
        mocked_serialized_value = MagicMock()
        mocked_instance = MagicMock()
        property = BaseProperty(Type)
        property.is_expression = MagicMock(return_value=False)
        property.is_env_var = MagicMock(return_value=True)
        mocked_property_value = MagicMock()
        property._values[mocked_instance] = mocked_property_value
        with patch('nio.types.Type.serialize',
                   return_value=mocked_serialized_value):
            serialized_value = property.serialize(mocked_instance)
        self.assertEqual(serialized_value, mocked_property_value.value)

    def test_deserialize_with_valid_value(self):
        property = BaseProperty(Type)
        value = 'value'
        self.assertEqual(value, property.deserialize(value))
