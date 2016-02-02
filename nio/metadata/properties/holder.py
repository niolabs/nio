from nio.metadata.properties.base import BaseProperty
from nio.metadata.properties.timedelta import TimeDeltaProperty
from nio.common.versioning.check import compare_versions, \
    VersionCheckResult, InvalidVersionFormat, is_version_valid, \
    get_major_version
from nio.metadata.environment import is_environment_var


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

    """ Functionality to group all properties of a given class.
    Provides methods to serialize and deserialize a given instance, and
    to obtain the description at the class level.

    Serializing an instance is useful when saving instance settings
    De-serializing an instance is useful when loading instance settings
    Obtaining a description is useful when exposing the class properties

    """

    def to_dict(self):
        """ Returns a dictionary representation of itself

        Args:
            None

        Returns:
            Instance serialization as a dictionary

        """
        class_properties = self.__class__.get_class_properties()
        return {property_name: prop.serialize(self)
                for (property_name, prop) in class_properties.items()}

    @classmethod
    def validate_dict(cls, properties):
        """ Validates the given property dictionary by successively
        de-serializing each property, returning the resulting (validated)
        property dictionary. If no exceptions are thrown here, all
        properties are valid.

        Args:
            properties (dict): values to validate

        Returns:
            properties (dict): validated and serialized

        """
        from nio.metadata.properties.list import ListProperty

        class_properties = cls.get_class_properties()

        for (property_name, prop) in class_properties.items():
            if property_name in properties:
                value = properties[property_name]

                from nio.metadata.properties.object import ObjectProperty

                # if it's an ObjectProperty, use the enclosed type and
                # validate the incoming config.
                if isinstance(prop, ObjectProperty):
                    value = prop.kwargs["obj_type"].validate_dict(value)

                # if the property is a list, validate it's members only if they
                # are PropertyHolders (i.e. ObjectProperty's)
                elif isinstance(prop, ListProperty):
                    list_obj_type = prop.kwargs["list_obj_type"]
                    if issubclass(list_obj_type, PropertyHolder):
                        for idx, item in enumerate(value):
                            value[idx] = list_obj_type.validate_dict(item)

                # ignore TimeDeltaProperty in order to avoid passing env
                # variables to
                elif isinstance(prop, TimeDeltaProperty):
                    pass

                # otherwise, unless the value is an environment variable,
                # validate it against the corresponding property by
                # de-serializing and serializing it.
                elif not is_environment_var(value):
                    # Let's make a fake property holder, to contain this
                    # property. That way, we can assign the value and make
                    # sure everything is good.
                    #
                    # TODO: Make it so we can serialize/deserialize at the
                    # property class level
                    tmp_inst = PropertyHolder()
                    prop.__set__(tmp_inst, prop.deserialize(value))
                    value = prop.serialize(tmp_inst)

                properties[property_name] = value

        return properties

    def from_dict(self, properties, logger=None):
        """ Loads properties from the specified dict into the instance.
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
                # if the given property was included in the input dictionary,
                # deserialize the dictionary's value and set it
                #value = prop.deserialize(properties[property_name])
                #setattr(self, property_name, value)
                # TODO: do we need to call deserialize first?
                setattr(self, property_name, properties[property_name])

                if hasattr(prop, "deprecated") and logger:
                    logger.info("Property: {0} is deprecated")

    @classmethod
    def get_description(cls):
        """ Provides the instance properties.

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
        """ Determines the instance properties and their default values.

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
        """ Determines the instance properties and their serializable defaults.

        Args:
            None

        Returns:
            (dict): The serializable default values for all properties, indexed
                by name.
        """
        properties = cls.get_class_properties()
        #TODO not calling serialzing on expressions and env_vars needs to
        # be somewhere else
        return {prop_name: prop.type.serialize(prop.default, **prop.kwargs)
                for prop_name, prop in properties.items()
                if prop.default and \
                not prop.is_expression(prop.default) and \
                not prop.is_env_var(prop.default)}

    @classmethod
    def get_class_properties(cls):
        """ Determines the metadata properties on this class by
        means of reflection. This is useful in serialization and
        deserialization.

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
        """ Determine version relation of an instance with respect to class
        version definition.

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
        if comparison_result == VersionCheckResult.Equal \
                or comparison_result == VersionCheckResult.Newer:
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
            if comparison_result == VersionCheckResult.Equal \
                    or comparison_result == VersionCheckResult.Newer:
                # ok, got a version not older than minimum
                pass
            else:
                raise OlderThanMinVersion(instance_version,
                                          min_version)
