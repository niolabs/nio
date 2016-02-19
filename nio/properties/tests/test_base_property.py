from unittest.mock import MagicMock

from nio.properties import BaseProperty
from nio.types import Type
from nio.util.support.test_case import NIOTestCase


class TestBaseProperty(NIOTestCase):

    def _value_passthrough(self, value, **kwargs):
        return value

    def test_set_and_get_value(self):
        type = Type
        instance = MagicMock()
        property = BaseProperty(type)
        set_values = ["", "string", 1, {}, []]
        get_values = []
        for set_value in set_values:
            property.__set__(instance, set_value)
            get_value = property.__get__(instance, MagicMock())
            get_values.append(get_value())
        self.assertEqual(set_values, get_values)

    def test_setting_invalid_value(self):
        """ Setting of an invalid value is allowed

        Type checking does not happen until the PropertyValue is called.

        """
        type = Type
        instance = MagicMock()
        property = BaseProperty(type)
        set_value = None
        property.__set__(instance, set_value)
        get_value = property.__get__(instance, MagicMock())
        with self.assertRaises(Exception):
            get_value()

    def test_allow_none(self):
        type = Type
        instance = MagicMock()
        property = BaseProperty(type, allow_none=True)
        set_value = None
        property.__set__(instance, set_value)
        get_value = property.__get__(instance, MagicMock())
        self.assertEqual(set_value, get_value())

    def test_serialize(self):
        type = Type
        instance = MagicMock()
        property = BaseProperty(type)
        value = 'value'
        property.__set__(instance, value)
        self.assertEqual(value, property.serialize(instance))

    def test_deserialize(self):
        type = Type
        property = BaseProperty(type)
        value = 'value'
        self.assertEqual(value, property.deserialize(value))
