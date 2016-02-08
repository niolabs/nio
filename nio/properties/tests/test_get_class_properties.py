import unittest

from nio.properties import PropertyHolder
from nio.properties import StringProperty


# noinspection PyProtectedMember
class TestProperties(unittest.TestCase):
    """ These tests check that PropertyHolder
    correctly returns the list of properties
    for different hierarchy 'shapes'
    """

    def test_parent_child(self):
        class ParentClass(PropertyHolder):
            parent_property = StringProperty(default="str")

        class ChildClass(ParentClass):
            child_property = StringProperty()

        child = ChildClass()
        # get class properties
        properties = child.get_class_properties()
        self.assertEqual(len(properties), 2)
        self.assertTrue("child_property" in properties)
        self.assertTrue("parent_property" in properties)

    def test_three_levels(self):
        class TopLevel(PropertyHolder):
            top_property = StringProperty(default="str")

        class MiddleLevel(TopLevel):
            middle_property = StringProperty()

        class BottomLevel(MiddleLevel):
            bottom_property = StringProperty()

        child = BottomLevel()
        # get class properties
        properties = child.get_class_properties()
        self.assertEqual(len(properties), 3)
        self.assertTrue("top_property" in properties)
        self.assertTrue("middle_property" in properties)
        self.assertTrue("bottom_property" in properties)

    def test_diamond_shape(self):
        class TopLevel(PropertyHolder):
            top_property = StringProperty(default="str")

        class MiddleLevel1(TopLevel):
            middle1_property = StringProperty()

        class MiddleLevel2(TopLevel):
            middle2_property = StringProperty()

        class BottomLevel(MiddleLevel1, MiddleLevel2):
            bottom_property = StringProperty()

        child = BottomLevel()
        # get class properties
        properties = child.get_class_properties()
        self.assertEqual(len(properties), 4)
        self.assertTrue("top_property" in properties)
        self.assertTrue("middle1_property" in properties)
        self.assertTrue("middle2_property" in properties)
        self.assertTrue("bottom_property" in properties)

    def test_parent_child_override(self):
        class ParentClass(PropertyHolder):
            parent_property = StringProperty(default="str")

        class ChildClass(ParentClass):
            parent_property = StringProperty(default="child")

        child = ChildClass()
        # get class properties
        properties = child.get_class_properties()
        self.assertEqual(len(properties), 1)
        self.assertTrue("parent_property" in properties)
        self.assertEqual(properties.get("parent_property").default, "child")
