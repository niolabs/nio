import datetime
from enum import Enum
import inspect
import sys
from nio.types import BoolType, DictType, FileType, FloatType,  IntType, \
    ListType, SelectType, StringType, TimeDeltaType
from nio.types.base import Type
from nio.util.support.test_case import NIOTestCase


NOW = datetime.datetime.utcnow()


class SampleEnum(Enum):
    red = 1
    green = 2
    blue = 3


class NotStringable(object):
    def __str__(self):
        raise Exception('This is not a string')


class TestTypes(NIOTestCase):

    def test_static_class(self):
        """A Type should never be instantiated."""
        with self.assertRaises(RuntimeError):
            Type()

    def test_serialize_deserialize_regular_types(self):
        """serialize then deserialize returns input value for all type."""
        types = {
            Type: [("string", "string"), (1, 1), (1.23, 1.23), (True, True)],
            BoolType: [(True, True), (False, False), (1, True)],
            DictType: [({}, {}), ({"key": "value"}, {"key": "value"})],
            FileType: [],
            FloatType: [(1.23, 1.23), (1, 1.0)],
            IntType: [(1, 1), (2, 2), (3, 3)],
            ListType: [], # tested seperately because of list_obj_type kwarg
            SelectType: [], # tested seperately because of enum kwarg
            StringType: [("string", "string")],
            TimeDeltaType: [
                (NOW, NOW),
                ({"seconds": 1}, datetime.timedelta(0, 1)),
                ({"minutes": 1}, datetime.timedelta(0, 60)),
            ],
        }
        for type_ in types:
            for value, result in types[type_]:
                serialized_value = type_.serialize(value)
                deserialized_value = type_.deserialize(serialized_value)
                self.assertEqual(deserialized_value, result)
                self.assertEqual(type(deserialized_value), type(result))

    def test_invalid_types(self):
        """Raise TypeError on deserialize of invalid values."""
        types = {
            Type: [],
            BoolType: [],
            DictType: ['not a dict'],
            FileType: [],
            FloatType: ['not a float'],
            IntType: ['not an int'],
            ListType: [], # tested seperately because of list_obj_type kwarg
            SelectType: [], # tested seperately because of enum kwarg
            StringType: [NotStringable()],
            TimeDeltaType: [],
        }
        for type_ in types:
            for value in types[type_]:
                with self.assertRaises(TypeError):
                    type_.deserialize(value)

    def test_serialize_deserialize_enum_type(self):
        """serialize then deserialize returns input value for enum type."""
        type_ = SelectType
        tests = [
            (SampleEnum.red, SampleEnum.red, SampleEnum),
            ('red', SampleEnum.red, SampleEnum),
        ]
        for value, result, enum_type in tests:
            deserialized_value = type_.deserialize(
                type_.serialize(value, enum=enum_type),
                enum=enum_type
            )
            self.assertEqual(deserialized_value, result)
            self.assertEqual(type(deserialized_value), type(result))

    def test_serialize_deserialize_list_type(self):
        """serialize then deserialize returns input value for list type."""
        type_ = ListType
        tests = [
            (["string", 1, 1.23, True], ["string", 1, 1.23, True], Type),
            (["string", "str"], ["string", "str"], StringType),
        ]
        for value, result, list_obj_type in tests:
            deserialized_value = type_.deserialize(
                type_.serialize(value, list_obj_type),
                list_obj_type
            )
            self.assertEqual(deserialized_value, result)
            self.assertEqual(type(deserialized_value), type(result))
