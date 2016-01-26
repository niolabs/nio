from nio.metadata.properties.old_base import AllowNoneViolation
from nio.metadata.properties.holder import PropertyHolder
from nio.metadata.properties.string import StringProperty
from nio.util.support.test_case import NIOTestCase


class Properties(PropertyHolder):
    # Note, property name and receiving property have to match
    allow_none_property = StringProperty(default="str", allow_none=True)
    not_allow_none_property = StringProperty(default="str", allow_none=False)
    try:
        invalid_not_allow_none_property = StringProperty(default=None,
                                                         allow_none=False)
        assert False
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
        with self.assertRaises(AllowNoneViolation):
            properties.not_allow_none_property = None

        # verify good assignments
        properties.allow_none_property = "Some String 1"
        properties.not_allow_none_property = "Some String 2"

    def test_from_dict(self):
        properties_to_set = {
            "allow_none_property": "str1",
            "not_allow_none_property": None
        }

        properties = Properties()
        properties.from_dict(properties_to_set)
