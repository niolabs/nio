"""

  Command Security decorator

"""

from nio.common.command.security.command import SecureCommand
from nio.modules.security.condition import SecureCondition


def command_security(name, all_conditions, *conditions):
    """ Decorator for defining a command that requires security

    Args:
        name (str): Command name
        all_conditions (bool): True to validate all conditions are met
           before the command can be executed
        conditions (list): List of conditions (methods returning boolean)
    """

    def wrap_command_security(cls):
        sec_cond = SecureCondition(name, all_conditions, conditions)
        # TODO: Check if cls is CommandHolder
        cmd = cls.get_commands_entry().get(name)
        if cmd is not None:
            sec_cmd = SecureCommand(cmd.name, sec_cond, cmd.title)
            for param in cmd.parameters:
                sec_cmd.add_parameter(param)
        else:
            sec_cmd = SecureCommand(name, sec_cond)
        cls.add_command(sec_cmd)
        return cls
    return wrap_command_security
