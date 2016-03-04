from nio.command.params.base import Parameter
from nio.command.params.string import StringParameter
from nio.modules.security.authorizer import Authorizer, Unauthorized
from nio.modules.security.task import SecureTask


class InvalidCommandArg(Exception):
    pass


class MissingCommandArg(Exception):
    pass


class Command(object):

    """Command to be used in CommandHolders (Blocks and Services).

    Commands can be secured with security modules SecureTask. An executing user
    with be authorized against the list of SecureTasks and then command will
    only be invoked if the user has permission.
    If ``meet_all`` is True, then the user needs to be authorized for every
    SecureTask. If False, then the user only needs to be authorized for one.

    Default security is ``SecureTask('commands.execute')``, but security can be
    removed from a command by passing an empty list as ``tasks``.

    Args:
        name (str): The name of the command. Should be the same as the name of
            the corresponding method.
        params (Properties): List of Property Params that are part of the
            command
        title (str): An optionally more detailed description of the
            command. If left blank, title defaults to name.
        method (str): The name of the real method exposed by this command if
            different than name
        tasks (list): List of SecureTask
        meet_all (bool): True to validate all tasks are met before the command
            can be executed

    """

    def __init__(self, name, *params, title=None, method=None,
                 tasks=None, meet_all=True):
        self._name = name
        self._parameters = []
        for p in params:
            self._add_parameter(p)
        self._title = title or name
        self._method = method or name
        if tasks is None:
            # Defult security if none is specified
            self._tasks = [SecureTask('commands.execute')]
        else:
            self._tasks = tasks
        self._meet_all = meet_all

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
    def method(self):
        return self._method

    def get_description(self):
        """Returns a description for a command instance.

        This method is used iteratively in CommandHolder.get_description.

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

    def _add_parameter(self, param):
        if isinstance(param, Parameter):
            self._parameters.append(param)
        else:
            raise RuntimeError("Invalid command parameter type: '{}'".format(
                getattr(param, 'name', param)))

    def collect_arguments(self, args):
        """Format passed arguments into parameter args and kwargs.

        Assign values to the command's parameters. This is done to
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
                raw_val = args.get(p.name) or p.default
                if raw_val is not None or p.allow_none:
                    val = p.deserialize(raw_val)
                    result.append(val)
                else:
                    raise MissingCommandArg(
                        "Command {}: missing argument {}".format(
                            self.name, p.name))
            # Now that we have all params that were not passed but have
            # default value covered, lets check for unrecognized param passed
            invalid_args = [arg for arg in args if arg not in
                            [p.name for p in self._parameters]]
            # Treat all extra args in the passed dict as kwargs
            for arg in invalid_args:
                result_kwargs[arg] = args.get(arg)
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
        """Check if the user specified meets the security conditions."""
        if not self._tasks:
            # If no SecureTasks are defined then it's not secure
            return True
        if user is None:
            return False
        try:
            Authorizer.authorize_multiple(
                user, *self._tasks, meet_all=self._meet_all)
            return True
        except Unauthorized:
            return False
