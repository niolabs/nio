"""
    Base Command class

"""
from nio.common.command.params.string import StringParameter
from nio.common.command.params.typed import TypedParameter


class InvalidCommandArg(Exception):
    pass


class MissingCommandArg(Exception):
    pass


class Command(object):

    """ The basic Command object. Maintains metadata for command methods
    implemented in Blocks and Services.

    Args:
        name (str): The name of the command. Should be the same as the
            name of the corresponding method.
        title (str): An optionally more detailed description of the
            command. If left blank, title defaults to name.
        method (str): The name of the real method exposed by this command if
            different than name

    """

    def __init__(self, name, title=None, method=None):
        self._name = name
        self._title = title or name
        self._parameters = []
        self._accept_kwargs = False
        self._method = method or name

    @property
    def name(self):
        return self._name

    @property
    def title(self):
        return self._title

    @property
    def parameters(self):
        return self._parameters

    @property
    def accept_kwargs(self):
        return self._accept_kwargs

    @accept_kwargs.setter
    def accept_kwargs(self, accept):
        self._accept_kwargs = accept

    @property
    def method(self):
        return self._method

    def get_description(self):
        """ Returns a description for a command instance.
        This method is used iteratively in CommandHolder.get_description.

        Args:
            None

        Returns:
            description (dict): the title of the command and descriptions
                of its parameters

        """
        description = {"title": self.title}
        params = {}
        for p in self._parameters:
            params[p.name] = p.get_description()
        description["params"] = params
        return description

    def add_parameter(self, param):
        """ Add a parameter to this command. Parameters should be added
        in the order they appear in the corresponding method prototype.

        Args:
            param (TypedParameter): The parameter to add.

        Returns:
            None

        """
        if isinstance(param, TypedParameter):
            self._parameters.append(param)
        else:
            raise RuntimeError(
                "Invalid command parameter type: '%s'" %
                getattr(param, 'name', param))

    def collect_arguments(self, args):
        """ Assign values to the command's parameters. This is done to
        provide safe conversion of command arguments from strings (they
        will likely arrive as strings in an HTTP request body) and to
        ensure that arguments are of the correct types.

        This method converts each argument to the appropriate type per
        each parameter. Collection fails if, for any parameter, allow_none
        is false and the type conversion returns None.

        Args:
            args (dict): The arguments.

        Returns:
            args (list): The list of arguments, converted and type
                checked.

        """
        result = []
        result_kwargs = {}
        if isinstance(args, dict):

            # Find and convert each param needed
            for p in self._parameters:
                val = p.convert(args.get(p.name))
                if val is not None or p._allow_none:
                    result.append(val)
                else:
                    raise MissingCommandArg(
                        "Command %s: missing argument %s" % (self.name, p.name)
                    )
            # Now that we have all params that were not passed but have
            # default value covered, lets check for unrecognized param passed
            invalid_args = [arg for arg in args if arg not in
                            [p.name for p in self._parameters]]
            if invalid_args:
                if self.accept_kwargs:
                    # Treat all args in the passed dict as kwargs
                    for arg in invalid_args:
                        result_kwargs[arg] = args.get(arg)
                else:
                    raise InvalidCommandArg(
                        "Invalid arguments passed: {0}".format(invalid_args))
        else:
            # Try to use whole arg as the param if the method only
            # needs one
            if len(self._parameters) == 1 and \
                    self._parameters[0].__class__ == StringParameter:
                result.append(args)
            else:
                raise InvalidCommandArg(
                    "Invalid arguments (dict expected): {0}".format(args))
        return result, result_kwargs

    def can_invoke(self, user):
        """ Evaluates if user can perform the command

        """
        return True
