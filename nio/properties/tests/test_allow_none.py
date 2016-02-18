from nio.properties.exceptions import AllowNoneViolation
from nio.properties.holder import PropertyHolder
from nio.properties import StringProperty
from nio.util.support.test_case import NIOTestCase


class Properties(PropertyHolder):
    # Note, property name and receiving property have to match
    allow_none_property = StringProperty(default="str", allow_none=True)
    not_allow_none_property = StringProperty(default="str", allow_none=False)
    try:
        pass
        # TODO: do we really need a default value if allow_none is False?
        #invalid_not_allow_none_property = StringProperty(default=None,
        #                                                 allow_none=False)
        #assert False
    except AllowNoneViolation:
        pass


class TestAllowNone(NIOTestCase):

    def test_initialization(self):
        properties = Properties()
        # make sure valid definitions are in the class
        self.assertIsNotNone(properties.allow_none_property)
        self.assertIsNotNone(properties.not_allow_none_property)
        # make sure invalid definition does not make it to the class
        with self.assertRaises(AttributeError):
            properties.invalid_not_allow_none_property

    def test_assignments(self):
        properties = Properties()
        # None assignments
        properties.allow_none_property = None
        # You can set None
        properties.not_allow_none_property = None
        with self.assertRaises(Exception):
            # TODO: should raise AllowNoneViolation
            # But you can't get the value if it's None
            properties.not_allow_none_property()
        # verify good assignments
        properties.allow_none_property = "Some String 1"
        properties.not_allow_none_property = "Some String 2"

    from unittest import skip
    @skip('TODO')
    def test_none_expression_violation(self):
        """ Expressions that evaluate to None """
        properties = Properties()
        properties.allow_none_property = "{{ None }}"
        properties.allow_none_property()
        properties.not_allow_none_property = "{{ None }}"
        with self.assertRaises(AllowNoneViolation):
            properties.not_allow_none_property()

    def test_from_dict_valid(self):
        properties_to_set = {
            "allow_none_property": None,
            "not_allow_none_property": "str1"
        }
        properties = Properties()
        properties.from_dict(properties_to_set)

    def test_from_dict_invalid(self):
        properties_to_set = {
            "allow_none_property": "str1",
            "not_allow_none_property": None
        }
        properties = Properties()
        properties.from_dict(properties_to_set)
        with self.assertRaises(Exception):
            # TODO: should raise AllowNoneViolation
            properties.validate_dict(properties_to_set)
