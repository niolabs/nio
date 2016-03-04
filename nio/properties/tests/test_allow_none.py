from nio.properties.exceptions import AllowNoneViolation
from nio.properties.holder import PropertyHolder
from nio.properties import StringProperty
from nio.testing.test_case import NIOTestCaseNoModules


class Properties(PropertyHolder):
    allow_none_property = StringProperty(default="str", allow_none=True)
    not_allow_none_property = StringProperty(default="str", allow_none=False)
    no_default_not_allow_none_property = StringProperty(default=None,
                                                        allow_none=False)


class TestAllowNone(NIOTestCaseNoModules):

    def test_initialization(self):
        """Properties should exist regardless of allow_none setting."""
        properties = Properties()
        # make sure valid definitions are in the class
        self.assertIsNotNone(properties.allow_none_property)
        self.assertIsNotNone(properties.not_allow_none_property)
        self.assertIsNotNone(properties.no_default_not_allow_none_property)

    def test_assignments(self):
        """Properties can be assigned any value, including None."""
        properties = Properties()
        # You can set None even if None isn't allowed
        properties.allow_none_property = None
        properties.not_allow_none_property = None
        properties.no_default_not_allow_none_property = None
        # Verify good assignments
        properties.allow_none_property = "Some String 1"
        properties.not_allow_none_property = "Some String 2"
        properties.no_default_not_allow_none_property = "Some String 3"

    def test_property_value_call(self):
        """Raise AllowNoneViolation if value is None."""
        properties = Properties()
        # You can set None even if None isn't allowed
        properties.allow_none_property = None
        properties.not_allow_none_property = None
        with self.assertRaises(AllowNoneViolation):
            # But you can't get the value if it's None
            properties.not_allow_none_property()
        with self.assertRaises(AllowNoneViolation):
            properties.no_default_not_allow_none_property()

    def test_none_expression_violation(self):
        """Raise AllowNoneViolation if expression evaluates to None."""
        properties = Properties()
        properties.allow_none_property = "{{ None }}"
        properties.allow_none_property()
        properties.not_allow_none_property = "{{ None }}"
        with self.assertRaises(AllowNoneViolation):
            properties.not_allow_none_property()

    def test_from_dict_and_validate(self):
        """Validation of PropertyHolder pases if allow_none is valid."""
        properties_to_set = {
            "allow_none_property": None,
            "not_allow_none_property": "str1",
            "no_default_not_allow_none_property": "str2",
        }
        properties = Properties()
        properties.from_dict(properties_to_set)
        # validation passes
        Properties.validate_dict(properties_to_set)
        properties.validate()

    def test_from_dict_invalid(self):
        """Validation of PropertyHolder fails if allow_none is violated."""
        properties_to_set = {
            "allow_none_property": "str1",
            "not_allow_none_property": None
        }
        properties = Properties()
        # From_dict will set anything
        properties.from_dict(properties_to_set)
        # But validate should catch the None value
        with self.assertRaises(AllowNoneViolation):
            Properties.validate_dict(properties_to_set)
        with self.assertRaises(AllowNoneViolation):
            properties.validate()
