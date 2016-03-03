from copy import deepcopy
from datetime import timedelta
from unittest.mock import MagicMock

from nio.properties import FloatProperty
from nio.properties import IntProperty
from nio.properties import ListProperty
from nio.properties import ObjectProperty
from nio.properties import PropertyHolder
from nio.properties import StringProperty
from nio.properties import TimeDeltaProperty
from nio.types import Type, IntType
from nio.util.support.test_case import NIOTestCaseNoModules


class ContainedClass(PropertyHolder):
    # Note, property name and receiving property have to match
    string_property = StringProperty(default="str")
    int_property = IntProperty(default=5)
    float_property = FloatProperty(default=5.0)


class ContainerClass(PropertyHolder):
    # Note, property name and receiving property have to match
    string_property = StringProperty(default='')
    int_property = IntProperty(default=0)
    float_property = FloatProperty(default=0.0)
    object_property = ObjectProperty(ContainedClass, default=ContainedClass())
    typed_list_property = ListProperty(Type, default=[])
    list_property = ListProperty(ContainedClass, default=[])
    td_property = TimeDeltaProperty(default={"seconds":0})


class TestProperties(NIOTestCaseNoModules):

    def test_initialization(self):
        """Make sure properties are in the class."""
        container = ContainerClass()
        self.assertIsNotNone(container.string_property)
        self.assertIsNotNone(container.int_property)
        self.assertIsNotNone(container.float_property)
        self.assertIsNotNone(container.object_property)
        self.assertIsNotNone(container.list_property)

    def test_validate_dict_when_invalid(self):
        """Raise exceptions when property holder is not valid."""
        container = ContainerClass

        with self.assertRaises(TypeError):
            container.validate_dict({'int_property': 'foo'})

        with self.assertRaises(TypeError):
            container.validate_dict({'float_property': 'foo'})

        with self.assertRaises(TypeError):
            container.validate_dict({
                'list_property': [{'int_property': 'foo'}]
            })

        with self.assertRaises(TypeError):
            container.validate_dict({
                'object_property': {
                    'int_property': 'bar'
                }
            })

        with self.assertRaises(TypeError):
            container.validate_dict({
                'object_property': {
                    'float_property': 'bar'
                }
            })

        with self.assertRaises(TypeError):
            container.validate_dict({
                'td_property': {'hectacres': 23}
            })

    def test_validate_dict_when_valid(self):
        """Valid dicts return serialized version of dict."""
        container = ContainerClass
        valid_dict = {'int_property': 1}
        self.assertDictEqual(container.validate_dict(deepcopy(valid_dict)),
                             valid_dict)
        valid_dict = {'float_property': 1.34}
        self.assertDictEqual(container.validate_dict(deepcopy(valid_dict)),
                             valid_dict)
        valid_dict = {
            'list_property': [{'int_property': 2}]
        }
        self.assertDictEqual(container.validate_dict(deepcopy(valid_dict)),
                             valid_dict)
        valid_dict = {
            'object_property': {
                'int_property': 1
            }
        }
        self.assertDictEqual(container.validate_dict(deepcopy(valid_dict)),
                             valid_dict)
        valid_dict = {
            'object_property': {
                'float_property': 1.34
            }
        }
        self.assertDictEqual(container.validate_dict(deepcopy(valid_dict)),
                             valid_dict)
        valid_dict = {
            'td_property': {'seconds': 23}
        }
        self.assertCountEqual(container.validate_dict(deepcopy(valid_dict)),
                             valid_dict)

        # validate object property
        valid_dict = {
            'object_property': {
                'int_property': "23",
                'float_property': "23.23",
                'string_property': 'bar',
            }
        }
        self.assertCountEqual(container.validate_dict(deepcopy(valid_dict)),
                             valid_dict)

        # make sure that the property holder passes validation
        # when there's an env var inside an object
        valid_dict = {
            'object_property': {
                'int_property': "[[SOMEINT]]",
                'string_property': 'bar',
            }
        }

        self.assertCountEqual(container.validate_dict(deepcopy(valid_dict)),
                             valid_dict)

    def test_accept_values(self):
        """Test that valid property values can be set and called."""
        container = ContainerClass()

        # assert that it takes values
        container.string_property = "String_Property_Value"
        container.int_property = 1
        container.float_property = 1.23
        contained = ContainedClass()
        contained.string_property = "contained string value"
        contained.int_property = 9
        contained.float_property = 9.23
        container.object_property = contained
        container.list_property = []
        contained_list = [contained]
        container.list_property = contained_list

        # assert that the values matched when reading them
        self.assertEqual(container.string_property(), "String_Property_Value")
        self.assertEqual(container.int_property(), 1)
        self.assertEqual(container.float_property(), 1.23)
        self.assertEqual(container.object_property(), contained)
        self.assertEqual(container.list_property(), contained_list)

    def test_delete_property(self):
        """Properties can't be deleted from holder."""
        container = ContainerClass()
        with self.assertRaises(AttributeError):
            del container.list_property

    def test_serialize_default(self):
        """Serialize holder returns default values."""
        default_properties = {"string_property": '',
                              "int_property": 0,
                              "float_property": 0.0,
                              "object_property": {
                                  "string_property": "str",
                                  "float_property": 5.0,
                                  "int_property": 5},
                              "typed_list_property": [],
                              "list_property": [],
                              "td_property": {
                                  'days': 0,
                                  'microseconds': 0,
                                  'seconds': 0}}

        container = ContainerClass()
        container_serialized = container.to_dict()

        # the serialized container should be set to default properties
        self.assertEqual(container_serialized, default_properties)

    def test_serialize_deserialize_matching(self):
        """Holders can serialize and deserialize and be the same."""

        properties_to_set = {
            "string_property": "str1",
            "int_property": 1,
            "float_property": 1.0,
            "object_property": {
                "string_property": "str2",
                "float_property": 2.0,
                "int_property": 2},
            "typed_list_property": ["a", "b", "c"],
            "list_property": [{
                "string_property": "str3",
                "float_property": 3.0,
                "int_property": 3}],
            "td_property": {
                "days": 1,
                "seconds": 1,
                "microseconds": 1}}

        # matching assignments with properties_to_set
        container1 = ContainerClass()
        container1.string_property = properties_to_set['string_property']
        container1.int_property = properties_to_set['int_property']
        container1.float_property = properties_to_set['float_property']
        contained = ContainedClass()
        contained.string_property = \
            properties_to_set['object_property']['string_property']
        contained.int_property = \
            properties_to_set['object_property']['int_property']
        contained.float_property = \
            properties_to_set['object_property']['float_property']
        container1.object_property = contained
        container1.td_property = timedelta(**properties_to_set['td_property'])
        container1.typed_list_property = \
            properties_to_set['typed_list_property']

        contained = ContainedClass()
        contained.string_property = \
            properties_to_set['list_property'][0]['string_property']
        contained.int_property = \
            properties_to_set['list_property'][0]['int_property']
        contained.float_property = \
            properties_to_set['list_property'][0]['float_property']
        container1.list_property = [contained]

        # the serialized container should match properties_to_set
        container1_serialized = container1.to_dict()
        self.assertEqual(container1_serialized['int_property'],
                         properties_to_set['int_property'])
        self.assertEqual(container1_serialized, properties_to_set)

        container2 = ContainerClass()
        # assign from dictionary
        container2.from_dict(properties_to_set, logger=MagicMock())
        container2_serialized = container2.to_dict()
        self.assertEqual(container1_serialized, container2_serialized)

    def test_description(self):
        """Description should exist for each property."""

        # access description from class
        description = ContainerClass.get_description()
        container1 = ContainerClass()
        container1.string_property = "StringPropertyValue"

        # access description from instance
        description1 = container1.get_description()

        # assert that descriptions do not depend on instance values
        self.assertEqual(description, description1)

        self.assertIn('string_property', description)
        self.assertIn('int_property', description)
        self.assertIn('float_property', description)
        self.assertIn('object_property', description)
        self.assertIn('string_property',
                      description['object_property']['template'])
        self.assertIn('int_property',
                      description['object_property']['template'])
        self.assertIn('float_property',
                      description['object_property']['template'])

        self.assertIn('list_property', description)
        self.assertIn('string_property',
                      description['list_property']['template'])
        self.assertIn('int_property',
                      description['list_property']['template'])
        self.assertIn('float_property',
                      description['list_property']['template'])

        alist = ListProperty(IntType)
        self.assertEqual('IntType', alist.description['template'])

    def test_additional_property_description(self):
        """Additional kwargs can be added to property description."""

        # test that anything we add to the property definition
        # find its way to the description
        class AdditionalDescriptionClass(PropertyHolder):
            property1 = StringProperty(bold=True,
                                       italics=True)

        description = AdditionalDescriptionClass.get_description()

        # check mandatory settings
        self.assertIn('title', description['property1'])
        self.assertIn('visible', description['property1'])
        self.assertIn('allow_none', description['property1'])

        # check added in arbitrary settings
        self.assertIn('bold', description['property1'])
        self.assertIn('italics', description['property1'])

    def test_print_property_info(self):
        """Property __str__ is overridden."""
        prop_info = str(StringProperty())
        from nio.types import StringType
        self.assertIn("type is: {}, args are".format(StringType), prop_info)
