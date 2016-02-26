from nio.command.base import Command
from nio.command.holder import CommandHolder


def command(*args, **kwargs):
    """Command decorator to add Commands to CommandHolders."""
    def wrap_command(cls):
        if not issubclass(cls, CommandHolder):
            raise TypeError("Must place command decorator on a CommandHolder")
        cls.add_command(Command(*args, **kwargs))
        return cls
    return wrap_command
