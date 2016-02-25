from unittest.mock import MagicMock, patch
from nio.properties.base import BaseProperty
from nio.properties.holder import PropertyHolder
from nio.types.base import Type
from nio.util.support.test_case import NIOTestCaseNoModules


class MockType(Type):
    # Need to make a new class to Mock since it's used a static class
    pass


class MyHolder(PropertyHolder):


    class MockBaseProperty(BaseProperty):
        def __init__(self):
            super().__init__(MockType)
            self.serialize = MagicMock(return_value='serialized value')
            self.deserialize = MagicMock(return_value='deserialized value')
            self.type.serialize = MagicMock(return_value='serialized value')

    property = MockBaseProperty()


class InvalidPropertyHolder(PropertyHolder):

    class MockBaseProperty(BaseProperty):
        def __init__(self):
            super().__init__(Type)
            self.serialize = MagicMock(return_value='serialized value')
            self.deserialize = MagicMock(side_effect=TypeError)

    property = MockBaseProperty()


class TestPropertyHolder(NIOTestCaseNoModules):

    def test_initialization(self):
        """Make sure definitions are in the class."""
        property_holder = MyHolder()
        self.assertIsNotNone(property_holder.property)

    def test_to_dict(self):
        """PropertyHolder.to_dict serializes each property."""
        property_holder = MyHolder()
        serialized = property_holder.to_dict()
        self.assertEqual(serialized, {"property": "serialized value"})
        MyHolder.__dict__['property'].\
            serialize.assert_called_with(property_holder)

    def test_from_dict(self):
        """PropertyHolder.from_dict sets each property."""
        property_holder = MyHolder()
        with patch('nio.properties.tests.test_property_holder.MyHolder.'
                   'MockBaseProperty.__set__') as mocked_property:
            property_holder.from_dict({"property": "new value"})
            mocked_property.assert_called_once_with(
                property_holder, 'new value')

    def test_validate(self):
        """PropertyHolder.validate does not raise exception when valid."""
        property_holder = MyHolder()
        validated = property_holder.validate()
        self.assertIsNone(validated)

    def test_validate_fail(self):
        """PropertyHolder.validate raises exception when invalid."""
        property_holder = InvalidPropertyHolder()
        with self.assertRaises(TypeError):
            property_holder.validate()

    def test_validate_dict_empty(self):
        """PropertyHolder.validate_dict does nothing with empty dict."""
        property_holder = MyHolder()
        validated = property_holder.validate_dict({})
        self.assertDictEqual(validated, {})

    def test_validate_dict_with_extra_props(self):
        """PropertyHolder.validate_dict does nothing with empty dict."""
        property_holder = MyHolder()
        validated = property_holder.validate_dict({"not_a_property": "?"})
        self.assertDictEqual(validated, {"not_a_property": "?"})

    def test_validate_dict_fail(self):
        """PropertyHolder.validate_dict raises deserialize TypeError."""
        property_holder = InvalidPropertyHolder()
        with self.assertRaises(TypeError):
            property_holder.validate_dict({"property": "invalid value"})
        InvalidPropertyHolder.__dict__['property'].\
            deserialize.assert_called_with('invalid value')
        # We never get to serialize since deserialize failed
        self.assertEqual(InvalidPropertyHolder.__dict__['property'].
                         serialize.call_count, 0)

    def test_validate_dict_as_classmethod(self):
        """PropertyHolder.validate_dict can be called as class method."""
        validated = MyHolder.validate_dict({"property": "valid value"})
        MyHolder.__dict__['property'].\
            deserialize.assert_called_with('valid value')
        MyHolder.__dict__['property'].\
            type.serialize.assert_called_with('valid value')
        self.assertDictEqual(validated, {"property": "serialized value"})

    def test_validate_dict_fail_as_classmethod(self):
        """PropertyHolder.validate_dict can be called as class method."""
        with self.assertRaises(TypeError):
            InvalidPropertyHolder.validate_dict({"property": "invalid value"})
        InvalidPropertyHolder.__dict__['property'].\
            deserialize.assert_called_with('invalid value')

    def test_delete_property(self):
        """Properties can't be deleted from a holder."""
        property_holder = MyHolder()
        with self.assertRaises(AttributeError):
            del property_holder.property

    def test_description(self):
        """PropertyHolder.get_description can be called as class method."""
        # access description from class
        class_description = MyHolder.get_description()
        property_holder = MyHolder()
        # access description from instance
        description = property_holder.get_description()
        # assert that descriptions do not depend on instance values
        self.assertEqual(class_description, description)

    def test_additional_property_description(self):
        """Anything added to the property definition go to the description."""
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
