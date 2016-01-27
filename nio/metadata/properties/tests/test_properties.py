from datetime import timedelta
from unittest.mock import MagicMock
from nio.metadata.properties.int import IntProperty
from nio.metadata.properties.float import FloatProperty
from nio.metadata.properties.list import ListProperty
from nio.metadata.properties.object import ObjectProperty
from nio.metadata.properties.holder import PropertyHolder
from nio.metadata.properties.string import StringProperty
from nio.metadata.properties.timedelta import TimeDeltaProperty
from nio.util.support.test_case import NIOTestCase


class ContainedClass(PropertyHolder):
    # Note, property name and receiving property have to match
    string_property = StringProperty(default="str")
    int_property = IntProperty(default=5)
    float_property = FloatProperty(default=5.0)


class ContainerClass(PropertyHolder):
    # Note, property name and receiving property have to match
    string_property = StringProperty()
    int_property = IntProperty(default=0)
    float_property = FloatProperty(default=0.0)
    object_property = ObjectProperty(ContainedClass)
    list_property = ListProperty(ContainedClass)
    td_property = TimeDeltaProperty()

    def __init__(self):
        super().__init__()


class TestProperties(NIOTestCase):

    def test_initialization(self):
        container = ContainerClass()
        # make sure definitions are in the class
        self.assertIsNotNone(container.string_property)
        self.assertIsNotNone(container.int_property)
        self.assertIsNotNone(container.float_property)
        self.assertIsNotNone(container.object_property)
        self.assertIsNotNone(container.list_property)

    def test_validate_dict(self):
        container = ContainerClass

        with self.assertRaises(ValueError):
            container.validate_dict({'int_property': 'foo'})

        with self.assertRaises(ValueError):
            container.validate_dict({'float_property': 'foo'})

        with self.assertRaises(ValueError):
            container.validate_dict({
                'list_property': [{'int_property': 'foo'}]
            })

        with self.assertRaises(ValueError):
            container.validate_dict({
                'object_property': {
                    'int_property': 'bar'
                }
            })

        with self.assertRaises(ValueError):
            container.validate_dict({
                'object_property': {
                    'float_property': 'bar'
                }
            })

        # validation of timedelta property gets skipped
        # bogus one will pass
        container.validate_dict({
            'td_property': {'hectares': 23}
        })

        legit_object = {
            'object_property': {
                'int_property': "23",
                'float_property': "23.23",
                'string_property': 'bar',
            }
        }

        props = container.validate_dict(legit_object)
        self.assertCountEqual(props, legit_object)

        # make sure that the property holder passes validation
        # when there's an env var inside an object
        legit_object_2 = {
            'object_property': {
                'int_property': "[[SOMEINT]]",
                'string_property': 'bar',
            }
        }

        props = container.validate_dict(legit_object_2)
        self.assertCountEqual(props, legit_object_2)

    def test_accept_values(self):
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

    def test_declines_wrong_types(self):
        container = ContainerClass()

        class NotStringable:
            def __str__(self):
                raise Exception("Not a string")

        # assert that it declines wrong types
        with self.assertRaises(TypeError):
            container.string_property = NotStringable()

        with self.assertRaises(TypeError):
            container.int_property = "string"

        with self.assertRaises(TypeError):
            container.float_property = 1

        with self.assertRaises(TypeError):
            container.object_property = 1

        with self.assertRaises(TypeError):
            container.object_property = ObjectProperty(int)

        with self.assertRaises(TypeError):
            container.list_property = "string"

        with self.assertRaises(AttributeError):
            del container.list_property

    def test_serialize_default(self):
        default_properties = {"string_property": "",
                              "int_property": 0,
                              "float_property": 0.0,
                              "object_property": {
                                  "string_property": "str",
                                  "float_property": 5.0,
                                  "int_property": 5},
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

        properties_to_set = {
            "string_property": "str1",
            "int_property": 1,
            "float_property": 1.0,
            "object_property": {
                "string_property": "str2",
                "float_property": 2.0,
                "int_property": 2},
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

        # access description from class
        description = ContainerClass.get_description()
        container1 = ContainerClass()
        container1.string_property = "StringPropertyValue"

        # access description from instance
        description1 = container1.get_description()

        # assert that descriptions do not depend on instance values
        self.assertEqual(description, description1)

        print(description)
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

        alist = ListProperty(int)
        self.assertEqual('int', alist.get_description()['template'])

    def test_additional_property_description(self):

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
        prop_info = str(StringProperty())
        self.assertIn("type is: str, args are", prop_info)
