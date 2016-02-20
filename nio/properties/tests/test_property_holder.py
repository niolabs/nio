from unittest.mock import MagicMock, patch
from nio.properties.base import BaseProperty
from nio.properties.holder import PropertyHolder
from nio.types.base import Type
from nio.util.support.test_case import NIOTestCase


class MyHolder(PropertyHolder):

    property = MagicMock(spec=BaseProperty)

    def __init__(self):
        self.property.__set__ = MagicMock()
        self.property.serialize.return_value = 'serialized value'
        self.property.deserialize.return_value = 'deserialized value'
        self.property.description = "property description"

    @classmethod
    def _validate_property_value(cls, prop, value):
        # Allow validation to pass
        pass


class InvalidPropertyHolder(PropertyHolder):

    property = MagicMock(spec=BaseProperty)


class TestPropertyHolder(NIOTestCase):

    def test_initialization(self):
        """ Make sure definitions are in the class """
        property_holder = MyHolder()
        self.assertIsNotNone(property_holder.property)

    def test_to_dict(self):
        """ PropertyHolder.to_dict serializes each property """
        property_holder = MyHolder()
        serialized = property_holder.to_dict()
        self.assertEqual(serialized, {"property": "serialized value"})
        property_holder.property.serialize.assert_called_once_with(
            property_holder)

    def test_from_dict(self):
        """ PropertyHolder.from_dict sets each property """
        property_holder = MyHolder()
        property_holder.from_dict({"property": "new value"})
        property_holder.property.__set__.assert_called_once_with(
            property_holder, 'new value')

    def test_validate(self):
        """ PropertyHolder.validate """
        property_holder = MyHolder()
        validation_status = property_holder.validate()
        self.assertDictEqual(validation_status, {"property": True})

    def test_validate_fail(self):
        """ PropertyHolder.validate """
        property_holder = InvalidPropertyHolder()
        validation_status = property_holder.validate()
        self.assertDictEqual(validation_status, {"property": False})

    def test_validate_dict_empty(self):
        """ PropertyHolder.validate_dict does nothing with empty dict """
        property_holder = MyHolder()
        validated = property_holder.validate_dict({})
        self.assertDictEqual(validated, {})

    def test_validate_dict_with_extra_props(self):
        """ PropertyHolder.validate_dict does nothing with empty dict """
        property_holder = MyHolder()
        validated = property_holder.validate_dict({"not_a_property": "?"})
        self.assertDictEqual(validated, {"not_a_property": "?"})
        # TODO: The way class attribues are bing mocked is messing this up
        #self.assertEqual(property_holder.property.deserialize.call_count, 0)
        #self.assertEqual(property_holder.property.serialize.call_count, 0)

    def test_validate_dict_fail(self):
        """ PropertyHolder.validate_dict raises deserialized exceptions """
        property_holder = InvalidPropertyHolder()
        InvalidPropertyHolder._validate_property_value = MagicMock(
            side_effect=TypeError)
        with self.assertRaises(TypeError):
            property_holder.validate_dict({"property": "invalid value"})
        property_holder._validate_property_value.assert_called_once_with(
            property_holder.property, 'invalid value')
        # We never get to serialize since deserialize failed
        self.assertEqual(property_holder.property.serialize.call_count, 0)

    def test_validate_dict_as_classmethod(self):
        """ PropertyHolder.validate_dict can be called as class method """
        with patch('nio.properties.base.BaseProperty',
                   spec=BaseProperty) as mocked_property:
            class StaticClassHolder(PropertyHolder):
                property = mocked_property
            # Let the property value validation pass
            StaticClassHolder._validate_property_value = MagicMock()
            mocked_property.serialize.return_value = 'serialized value'
            validated = \
                StaticClassHolder.validate_dict({"property": "valid value"})
            mocked_property.deserialize.assert_called_once_with('valid value')
            mocked_property.serialize.assert_called_once_with(
                StaticClassHolder)
        self.assertDictEqual(validated, {"property": "serialized value"})

    def test_validate_dict_fail_as_classmethod(self):
        """ PropertyHolder.validate_dict can be called as class method """
        with patch('nio.properties.base.BaseProperty',
                   spec=BaseProperty) as mocked_property:
            class StaticClassHolder(PropertyHolder):
                property = mocked_property
            # Let the property value validation pass
            StaticClassHolder._validate_property_value = MagicMock(
                side_effect=TypeError)
            with self.assertRaises(TypeError):
                StaticClassHolder.validate_dict({"property": "invalid value"})
            StaticClassHolder._validate_property_value.assert_called_once_with(
                mocked_property, 'invalid value')

    def test_delete_property(self):
        """ Properties can't be deleted from a holder """
        property_holder = MyHolder()
        with self.assertRaises(AttributeError):
            del property_holder.property

    def test_description(self):
        """ PropertyHolder.get_description can be called as class method """
        # access description from class
        class_description = MyHolder.get_description()
        property_holder = MyHolder()
        # access description from instance
        description = property_holder.get_description()
        # assert that descriptions do not depend on instance values
        self.assertEqual(class_description, description)

    def test_additional_property_description(self):
        # test that anything we add to the property definition
        # find its way to the description
        class AdditionalDescriptionClass(PropertyHolder):
            property = BaseProperty(Type, bold=True, italics=True)
        description = AdditionalDescriptionClass.get_description()
        # check mandatory settings
        self.assertIn('title', description['property'])
        self.assertIn('visible', description['property'])
        self.assertIn('allow_none', description['property'])
        self.assertIn('default', description['property'])
        # check added in arbitrary settings
        self.assertIn('bold', description['property'])
        self.assertIn('italics', description['property'])
