class Parameter(object):

    """ A typed command parameter. Base class for other parameters

    Examples of other command parameters are IntParameter, StringParameter, etc

    Args:
        type (Type): The type of data of this parameter.
        name (str): Name of the parameter. Used to look up arguments.
        title (str): More detailed description of the parameter
        default (str): default value to be used in
        allow_none (bool): does this parameter need a value?

    """

    def __init__(self, _type, name,
                 title=None, default=None, allow_none=False, **kwargs):
        self.type = _type
        self.name = name
        self.title = title or name
        self.default = default
        self.allow_none = allow_none
        self.kwargs = kwargs

    def get_description(self):
        """ Boilerplate description of the parameter.

        Args:
            None

        Returns:
            description (dict): The description.

        """
        return {
            "title": self.title,
            "default": self.default,
            "allow_none": self.allow_none
        }

    def deserialize(self, value, **kwargs):
        # Allow property kwargs to be overriden by call to serialize
        merged_kwargs = self.kwargs.copy()
        merged_kwargs.update(**kwargs)
        return self.type.deserialize(value, **merged_kwargs)
