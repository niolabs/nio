"""
    NIO Typed Parameter class

"""
from nio.command.params import Parameter


class TypedParameter(Parameter):

    """ A typed command parameter. Base class for other params
    (e.g. Int*, String*).

    Args:
        name (str): Name of the parameter. Used to look up arguments.
        title (str): More detailed description of the parameter
        default (str): default value to be used in
        allow_none (bool): does this parameter need a value?
        converter (function): a function for converting param
            values from strings to the desired type

    """

    def __init__(self, name, title, default, allow_none, converter):
        self._name = name
        self._title = title or name
        self._default = default
        self._allow_none = allow_none
        self._converter = converter

    @property
    def name(self):
        return self._name

    @property
    def title(self):
        return self._title

    def convert(self, val):
        """Convert the given value to the specified type/format. If
        the value is None, convert the specified default value. If the
        default value is None, do no conversion, returning None.

        Args:
            val (str): The value to be converted.

        Returns:
            value (varies): The converted value.

        """
        value = val or self._default
        if value is not None:
            value = self._converter(value)
        return value

    def get_description(self):
        """ Boilerplate description of the parameter.

        Args:
            None

        Returns:
            description (dict): The description.

        """
        return {
            "title": self.title,
            "default": self._default,
            "allow_none": self._allow_none
        }
