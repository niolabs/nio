import json

from nio.properties.holder import PropertyHolder, \
    OlderThanMinVersion, NoClassVersion, NoInstanceVersion
from nio.properties.version import VersionProperty, \
    InvalidVersionFormat
from nio.util.support.test_case import NIOTestCaseNoModules


class ClassWithNoVersion(PropertyHolder):
    pass


class ClassWithVersion(PropertyHolder):
    version = VersionProperty(default="1.1.1")


class ClassWithMinVersion(PropertyHolder):
    version = VersionProperty(default="2.2.2", min_version="1.1.1")


class ClassVersionInitialize(PropertyHolder):
    version_straight = VersionProperty("1.1.1")
    version_default = VersionProperty(default="1.1.2")
    version_both = VersionProperty("1.1.3", default="1.1.4")


class TestVersion(NIOTestCaseNoModules):
    def test_valid_versions(self):
        """ assert that it takes valid values
        """
        instance = ClassWithVersion()
        versions = ["1.2.3", "1.2.*", "1.*", "*", "1.1.1", "1.0.1rc1"]
        for version in versions:
            instance.version = version
            self.assertEqual(instance.version(), version)

    def test_invalid_versions(self):
        """ assert that it rejects invalid values
        """
        instance = ClassWithVersion()

        invalid_versions = ["1.k.3", "invalid.2.*", "not a version"]
        for invalid_version in invalid_versions:
            with self.assertRaises(InvalidVersionFormat):
                instance.version = invalid_version

    def test_serialize_matching(self):
        """ assert that a 360 conversion is valid
        first it does a "to_dict", then it does a "from_dict" and then a
        "to_dict" and compares against first "to_dict" result
        """
        properties_to_set = {"version": "1.4.1"}
        properties_serialized = {"version": "1.4.1"}

        # matching assignments with properties_to_set
        instance = ClassWithVersion()
        instance.version = properties_to_set['version']

        # the serialized container should match properties_to_set
        instance_serialized = instance.to_dict()
        self.assertEqual(instance_serialized, properties_serialized)

        instance2 = ClassWithVersion()
        # assign from dictionary
        instance2.from_dict(properties_serialized)
        instance2_serialized = instance2.to_dict()
        self.assertEqual(instance_serialized, instance2_serialized)

    def test_description(self):
        """ asserts that description is retrieved as expected
        """
        instance = ClassWithVersion()
        description = instance.get_description()
        description_json = json.dumps(description)
        self.assertIsInstance(json.loads(description_json), dict)
        self.assertIn('version', description)
        prop = description.get('version')
        self.assertIsNotNone(prop.get('default'))
        self.assertIsNone(prop.get('min_version'))

        instance = ClassWithMinVersion()
        description = instance.get_description()
        self.assertIn('version', description)
        prop = description.get('version')
        self.assertIsNotNone(prop.get('default'))
        self.assertIsNotNone(prop.get('min_version'))

    def test_deserialize(self):
        """ asserts for equality a deserialize call
        """
        prop = VersionProperty(default="1.1.1")
        self.assertEqual(prop.deserialize("1.1.1"), "1.1.1")

    def test_defaults(self):
        """ asserts that defaults are retrieved as expected
        """
        instance = ClassWithVersion()
        defaults = instance.get_defaults()
        self.assertIn('version', defaults)
        self.assertEqual(defaults['version'], "1.1.1")

    def test_min_version(self):
        properties_to_set = {"version": "1.0.1"}
        properties_serialized = {"version": "1.0.1"}

        instance = ClassWithMinVersion()
        instance.version = properties_to_set["version"]
        instance_serialized = instance.to_dict()

        instance2 = ClassWithMinVersion()
        # assign from dictionary
        instance2.from_dict(properties_serialized)
        instance2_serialized = instance2.to_dict()
        self.assertEqual(instance_serialized, instance2_serialized)

    def test_handle_versions(self):

        instance = ClassWithNoVersion()
        class_properties = instance.get_class_properties()
        instance_properties = {"version": "1.1.1"}
        with self.assertRaises(NoClassVersion):
            instance._handle_versions(class_properties, instance_properties)

        instance = ClassWithVersion()
        class_properties = instance.get_class_properties()

        instance_properties = {}
        with self.assertRaises(NoInstanceVersion):
            instance._handle_versions(class_properties, instance_properties)

        instance_properties = {"version": "1.1.1"}
        instance._handle_versions(class_properties, instance_properties)
        instance_properties = {"version": "1.2.1"}
        instance._handle_versions(class_properties, instance_properties)

        # older version, expect exception since there is no min_version to
        # check against
        instance_properties = {"version": "1.0.1"}
        # version newer than calculated default minimum
        instance._handle_versions(class_properties, instance_properties)

        instance_properties = {"version": "0.0.1"}
        # version older than calculated default minimum
        with self.assertRaises(OlderThanMinVersion):
            instance._handle_versions(class_properties, instance_properties)

        instance = ClassWithMinVersion()
        class_properties = instance.get_class_properties()
        # an older than default version is ok as long as it is newer than
        # min_version
        instance_properties = {"version": "1.1.5"}
        instance._handle_versions(class_properties, instance_properties)
        instance_properties = {"version": "1.0.1"}
        with self.assertRaises(OlderThanMinVersion):
            instance._handle_versions(class_properties, instance_properties)

    def test_process_and_log_version(self):
        """ Processes same tests as handle versions + ensuring that log
        statements are valid
        """

        import logging

        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger("test_version")

        instance = ClassWithNoVersion()
        class_properties = instance.get_class_properties()
        instance_properties = {"version": "1.1.1"}
        instance._process_and_log_version(class_properties,
                                          instance_properties, logger)

        instance = ClassWithVersion()
        class_properties = instance.get_class_properties()

        instance_properties = {}
        instance._process_and_log_version(class_properties,
                                          instance_properties, logger)

        instance_properties = {"version": "1.1.1"}
        instance._process_and_log_version(class_properties,
                                          instance_properties, logger)
        instance_properties = {"version": "1.2.1"}
        instance._process_and_log_version(class_properties,
                                          instance_properties, logger)

        # older version, expect exception since there is no min_version to
        # check against
        instance_properties = {"version": "1.0.1"}
        instance._process_and_log_version(class_properties,
                                          instance_properties, logger)

        instance = ClassWithMinVersion()
        class_properties = instance.get_class_properties()
        # an older than default version is ok as long as it is newer than
        # min_version
        instance_properties = {"version": "1.1.5"}
        instance._process_and_log_version(class_properties,
                                          instance_properties, logger)
        instance_properties = {"version": "1.0.1"}
        instance._process_and_log_version(class_properties,
                                          instance_properties, logger)

    def test_version_initialize(self):

        instance = ClassVersionInitialize()
        self.assertEqual(instance.version_straight(), "1.1.1")
        self.assertEqual(instance.version_default(), "1.1.2")
        self.assertEqual(instance.version_both(), "1.1.3")
