from unittest.mock import MagicMock
from nio.metadata.types.base import Type
from nio.metadata.types.string import StringType
from nio.util.support.test_case import NIOTestCase


class TestTypes(NIOTestCase):

    def test_string_type(self):
        value = "string"
        self.assertEqual(StringType.deserialize(StringType.serialize(value)),
                         value)

    def test_string_type_invalid(self):
        class NotStringable:
            def __str__(self):
                raise Exception('This is not a string')

        value = NotStringable()
        with self.assertRaises(Exception):
            StringType.deserialize(value)

    def test_static_class(self):
        """ A Type should never be instantiated """
        with self.assertRaises(RuntimeError):
            Type()
