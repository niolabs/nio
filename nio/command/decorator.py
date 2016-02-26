import inspect
from nio.command.base import Command
from nio.command.holder import CommandHolder


def command(name, *params, title=None, method=None, tasks=None, meet_all=True):
    """ Command decorator that exposes command Blocks and Services operations

    Args:
        name (str): The name of the command. Should be the same as the
            name of the corresponding method.
        params (Properties): List of Property Params that are part of the
            command
        title (str): An optionally more detailed description of the
            command. If left blank, title defaults to name.
        method (str): The name of the real method exposed by this command if
            different than name
        tasks (list): List of SecureTask
        meet_all (bool): True to validate all tasks are met
           before the command can be executed
    """
    def wrap_command(cls):
        if not issubclass(cls, CommandHolder):
            raise TypeError(
                "Must place command decorator on a CommandHolder")
        nio_command = Command(
            name, title=title, method=method, tasks=tasks, meet_all=meet_all)
        for p in params:
            nio_command.add_parameter(p)
        cls.add_command(nio_command)
        # Check if method accept kwargs
        f = getattr(cls, method or name, None)
        if inspect.ismethod(f) or inspect.isfunction(f):
            args = inspect.getargspec(f)
            nio_command.accept_kwargs = "kwargs" in args or \
                                        hasattr(args, 'defaults')
        return cls
    return wrap_command
