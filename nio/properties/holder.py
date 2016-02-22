from nio.util.versioning.check import compare_versions, \
    VersionCheckResult, InvalidVersionFormat, is_version_valid, \
    get_major_version
from nio.properties.base import BaseProperty
from nio.properties.util.property_value import PropertyValue


class NoClassVersion(Exception):
    pass


class NoInstanceVersion(Exception):

    def __init__(self, class_version):
        super().__init__()
        self.class_version = class_version


class OlderThanMinVersion(Exception):

    def __init__(self, instance_version, min_version):
        super().__init__()
        self.instance_version = instance_version
        self.min_version = min_version


class PropertyHolder(object):

    """ Support nio.properties.BaseProperty as class attribtes.

    Functionality to group all properties of a given class.
    Provides methods to serialize and deserialize a given instance, and
    to obtain the description at the class level.

    Serializing an instance is useful when saving instance settings
    De-serializing an instance is useful when loading instance settings
    Obtaining a description is useful when exposing the class properties

    """

    def to_dict(self):
        """ Return a dictionary representation of itself.

        Args:
            None

        Returns:
            Instance serialization as a dictionary

        """
        class_properties = self.__class__.get_class_properties()
        return {property_name: prop.serialize(self)
                for (property_name, prop) in class_properties.items()}

    def validate(self):
        """ Return dictionary of each property and it's validation status.

        Returns:
            dict: Values are True if valid, False otherwise.

            Example::
            {
                "valid_property": True,
                "invalid_property": False
            }

        """
        class_properties = self.__class__.get_class_properties()
        validation_status = {}
        for (property_name, prop) in class_properties.items():
            try:
                # Calling a PropertyValue is the best way to determine if a
                # value is valid. It checks allow_none violations and
                # deserializes (which checks type errors).
                getattr(self, property_name)()
                validation_status[property_name] = True
            except:
                validation_status[property_name] = False
        return validation_status

    @classmethod
    def validate_dict(cls, properties):
        """ Call and deserialize each input property to determine validity.

        Validates the given property dictionary by successively
        de-serializing each property, returning the resulting (validated)
        property dictionary. If no exceptions are thrown here, all
        properties are valid.

        Args:
            properties (dict): values to validate

        Returns:
            properties (dict): validated and serialized

        Raises:
            AllowNoneViolation: Property value does not allow none
            TypeError: Property value is invalid

        """
        class_properties = cls.get_class_properties()
        for (property_name, prop) in class_properties.items():
            if property_name in properties:
                value = properties[property_name]
                # Calling a PropertyValue is the best way to determine if a
                # value is valid. It checks allow_none violations and
                # deserializes (which checks type errors).
                PropertyValue(prop, value)()
                # Return the serialized version of the input dictionary
                serialized_value = prop.type.serialize(value, **prop.kwargs)
                properties[property_name] = serialized_value
        return properties

    def from_dict(self, properties, logger=None):
        """ Load properties from the specified dict into the instance.

        Note: Existing values for properties that are not included in
        the properties dict would remain.

        Args:
            properties (dict): values to assign to this instance

        Returns:
            None

        """
        # perform minimum validation
        if properties is None:
            raise TypeError()

        # Retrieve the list of all class properties
        class_properties = self.__class__.get_class_properties()
        self._process_and_log_version(class_properties, properties, logger)
        for (property_name, prop) in class_properties.items():
            if property_name in properties:
                setattr(self, property_name, properties[property_name])
                if hasattr(prop, "deprecated") and logger:
                    # TODO: test and document "deprecated" flag
                    logger.info("Property: {0} is deprecated")

    @classmethod
    def get_description(cls):
        """ Provide the instance properties.

        Args:
            None

        Returns:
            Instance description as a dictionary of properties

        """
        class_properties = cls.get_class_properties()
        descriptions = {property_name: prop.description
                        for (property_name, prop) in class_properties.items()}
        if hasattr(cls, "__version__") and "version" not in descriptions:
            descriptions["version"] = cls.__version__

        return descriptions

    @classmethod
    def get_defaults(cls):
        """ Determine the instance properties and their default values.

        Args:
            None

        Returns:
            (dict): The default values for all properties, indexed
                by name.
        """
        properties = cls.get_class_properties()
        return {prop_name: prop.default
                for prop_name, prop in properties.items()}

    @classmethod
    def get_serializable_defaults(cls):
        """ Determine the instance properties and their serializable defaults.

        Args:
            None

        Returns:
            (dict): The serializable default values for all properties, indexed
                by name.
        """
        properties = cls.get_class_properties()
        return {prop_name: prop.serialize(instance=cls)
                for prop_name, prop in properties.items()}

    @classmethod
    def get_class_properties(cls):
        """ Determine the metadata properties on this class.

        Determine the metadata properties on this class by means of reflection.
        This is useful in serialization and deserialization.

        Args:
            None

        Returns:
            class_properties (dict): The discovered properties, indexed
                by name.

        """
        class_attribute = "{0}_properties".format(cls.__name__)
        if not hasattr(cls, class_attribute):
            # find out properties
            properties = dict()
            import inspect
            classes = inspect.getmro(cls)
            for _class in classes:
                for (prop_name, prop) in _class.__dict__.items():
                    if (isinstance(prop, BaseProperty) and
                            prop_name not in properties):
                        properties[prop_name] = prop

            # cache properties
            setattr(cls, class_attribute, properties)
        return getattr(cls, class_attribute)

    def _process_and_log_version(self, class_properties, properties, logger):
        name = properties.get("name", "")
        try:
            self._handle_versions(class_properties, properties)
        except NoClassVersion:
            if logger:
                logger.warning('Class: {0} does not contain version info'.
                               format(self.__class__.__name__))
        except NoInstanceVersion as e:
            if logger:
                logger.warning('Instance {0} of class: {1} does not contain '
                               'version info, class version: {2}'.
                               format(name, self.__class__.__name__,
                                      e.class_version))
        except OlderThanMinVersion as e:
            if logger:
                logger.warning('Instance {0} version: {1} is older than'
                               ' minimum: {2}'.format
                               (name, e.instance_version, e.min_version))

    def _handle_versions(self, class_properties, instance_properties):
        """ Raise version exceptions based on instance config.

        Determine version relation of an instance with respect to class version
        definition.

        Assumes that both, class and instance refer to their version through
        a version property

        Args:
            class_properties: class properties
            instance_properties: instance properties as retrieved likely from
                configuration file.

        Raises:
            NoClassVersion
            NoInstanceVersion
            InvalidVersionFormat
            OlderThanMinVersion
        """

        try:
            class_version = class_properties.get("version").default
        except:
            raise NoClassVersion()

        # need to check against possible version stored in properties
        if "version" not in instance_properties:
            raise NoInstanceVersion(class_version)

        # compare versions and determine compatibility
        instance_version = instance_properties["version"]

        if not is_version_valid(instance_version):
            raise InvalidVersionFormat()

        comparison_result = compare_versions(instance_version,
                                             class_version)
        if comparison_result == VersionCheckResult.equal \
                or comparison_result == VersionCheckResult.newer:
            # instance has a newer version, it is ok
            pass
        else:
            # got an older version in the block, check if it passes
            # min version
            if "min_version" not in class_properties["version"].kwargs:
                # min_version by default is a major version, which is built
                # starting from the major digit, and adding zero's to it.
                min_version = get_major_version(class_version)
            else:
                min_version = \
                    class_properties["version"].kwargs["min_version"]

            comparison_result = compare_versions(instance_version,
                                                 min_version)
            if comparison_result == VersionCheckResult.equal \
                    or comparison_result == VersionCheckResult.newer:
                # ok, got a version not older than minimum
                pass
            else:
                raise OlderThanMinVersion(instance_version,
                                          min_version)
