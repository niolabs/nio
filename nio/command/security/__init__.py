"""

  Command Security decorator

"""
from nio.command.security.command import SecureCommand
from nio.command.holder import CommandHolder


def command_security(name, *tasks, meet_all=True):
    """ Decorator for defining a command that requires security

    Args:
        name (str): Command name
        tasks (list): List of tasks
        meet_all (bool): True to validate all tasks are met
           before the command can be executed
    """

    def wrap_command_security(cls):
        if not issubclass(cls, CommandHolder):
            raise TypeError(
                "Must place command_security decorator on a CommandHolder")

        cmd = cls.get_commands_entry().get(name)
        if cmd is not None:
            # Command already exists, just adding security
            sec_cmd = SecureCommand(
                cmd.name, *tasks, title=cmd.title, meet_all=meet_all)
            for param in cmd.parameters:
                sec_cmd.add_parameter(param)
        else:
            sec_cmd = SecureCommand(name, *tasks, meet_all=meet_all)
        cls.add_command(sec_cmd)
        return cls
    return wrap_command_security
