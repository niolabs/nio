from importlib import import_module
from nio.util.logging import get_nio_logger
from nio.util.versioning.check import compare_versions, VersionCheckResult


class DependsOn(object):

    """Decorator for setting a component version dependency on a component."""

    attribute_format = "{0}_dependencies"

    def __init__(self, dependency, version=None):
        """Defines the component version dependency on the decorated component.

        Args:
            dependency (string): the module that is a dependency of the
                                 decorated component.
            version (string): the required version of the dependency.

        """

        self.logger = get_nio_logger("Dependency")
        self._dependency = dependency
        self._version = version

    def __call__(self, cls):
        component_version = None

        # bother with version at all?
        if self._version:
            m = import_module(self._dependency)
            if hasattr(m, "__version__"):
                component_version = m.__version__
                if not validate_version(component_version, self._version):
                    self.logger.warning(
                        "'{}' dependency: '{}' not satisfied, version: '{}' "
                        "is installed and '{}' was requested".format(
                            cls.__name__, self._dependency, component_version,
                            self._version))
            else:
                self.logger.warning('Component: {0} does not contain '
                                    'version info'.
                                    format(self._dependency))

        # add to list of dependencies
        attribute = DependsOn.attribute_format.format(cls.__name__)
        if not hasattr(cls, attribute):
            setattr(cls, attribute, {})
        dependencies = getattr(cls, attribute)
        dependencies[self._dependency] = (component_version, self._version)

        return cls


def validate_version(component_version, dependency_version):
    """Check if a component's version is valid for a given dependency.

    Args:
        component_version (string): version of installed component.
        dependency_version (string): version required by dependency.

    Returns:
        bool: Returns True if valid, False if not.

    """

    # Any version set to None is considered valid for comparison
    # purposes once it gets this far
    if component_version is None or dependency_version is None:
        return True

    return compare_versions(component_version,
                            dependency_version).value >= \
        VersionCheckResult.older.value


def get_class_dependencies(cls):
    """Provides class dependencies.

    When parent classes have dependencies these are added simulating
    inheritance behaviour

    Args:
        cls (class type): the class.

    Returns:
        class dependencies defined using @DependsOn

    """
    attribute = DependsOn.attribute_format.format(cls.__name__)
    dependencies = {}
    for _class in cls.__bases__:
        dependencies.update(get_class_dependencies(_class))
    dependencies.update(getattr(cls, attribute, {}))

    return dependencies
