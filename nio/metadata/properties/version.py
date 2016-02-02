from nio.metadata.properties import StringProperty
from nio.common.versioning.check import is_version_valid, InvalidVersionFormat


class VersionProperty(StringProperty):
    """ Defines a Version property.
    Version property permits saving version information with
    (mayor.minor.build) format
    """

    def __init__(self, version=None, **kwargs):
        """ Initializes a version property.

        Keyword Args:
            Property definitions

        """
        if "default" in kwargs:
            if version is not None:
                # hmm, both version and default specified,
                # version argument overrides
                kwargs["default"] = version
            super().__init__(**kwargs)
        else:
            super().__init__(default=version, **kwargs)

    def __set__(self, instance, value):
        """ Override default set so that value can be checked against version
        valid format
        """

        # make sure value follows "mayor,minor,build" convention
        if not is_version_valid(value):
            raise InvalidVersionFormat("Version: {0} is invalid".format(value))

        super().__set__(instance, value)
