from nio.properties import PropertyHolder
from nio.properties import StringProperty
from nio.util.support.test_case import NIOTestCaseNoModules


class ClassWithoutVersion(PropertyHolder):
    string_property = StringProperty(default="ClassWithoutVersion")


class ClassWithVersion(PropertyHolder):
    __version__ = "version_test"
    string_property = StringProperty(default="ClassWithVersion")


class ClassWithVersionAsProperty(PropertyHolder):
    __version__ = "version_in_class"
    version = StringProperty(default="version_as_property")


class TestDefaults(NIOTestCaseNoModules):
    def test_description(self):
        """Testing that version is retrieved as expected."""
        without_version = ClassWithoutVersion.get_description()
        self.assertNotIn("version", without_version)

        with_version = ClassWithVersion.get_description()
        self.assertIn("version", with_version)
        self.assertEqual(with_version["version"], "version_test")

        with_version_as_property = ClassWithVersionAsProperty.get_description()
        self.assertIn("version", with_version_as_property)
        self.assertNotEqual(with_version_as_property["version"],
                            "version_in_class")
