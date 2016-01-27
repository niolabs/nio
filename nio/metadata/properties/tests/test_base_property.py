from unittest.mock import MagicMock
from nio.metadata.properties.base import BaseProperty
from nio.metadata.types.string import StringType
from nio.util.support.test_case import NIOTestCase


class TestBaseProperty(NIOTestCase):

    def test_base_property(self):
        type = MagicMock()
        property = BaseProperty(type)
        property.__set__(MagicMock(), MagicMock())
        property.__get__(MagicMock(), MagicMock())
        property.serialize(MagicMock())
        property.deserialize(MagicMock())

    def test_string_type(self):
        type = StringType()
        property = BaseProperty(type)
        instance = MagicMock()
        self.assertEqual(property.type, type)
        # Set a value on a property instance
        set_value = 'string'
        property.__set__(instance, set_value)
        # Get the value for that instance
        get_value = property.__get__(instance, MagicMock())
        self.assertEqual(set_value, get_value())
        # Get a value for a new instance
        get_value = property.__get__(MagicMock(), MagicMock())
        self.assertEqual(type.default, get_value())
