"""
    NIO Dictionary Parameter class

"""
from nio.command.params.typed import TypedParameter


class DictParameter(TypedParameter):
    """ A command parameter expecting a dictionary

    """
    def __init__(self, name, title=None, default={}, allow_none=False):
        super().__init__(name, title, default, allow_none, self._converter)

    def get_description(self):
        description = super().get_description()
        description['type'] = 'dict'
        return description

    @staticmethod
    def _converter(val):
        """ Allows conversion to a dict.
        """
        # if a string is passed, attempt to convert it to a dict
        if isinstance(val, str):
            import json
            # attempt to convert to json
            try:
                val = json.loads(val)
            except ValueError as e:
                # make message user friendlier
                raise ValueError("Converting string to dict, details: {0}".
                                 format(str(e)))

        return val
