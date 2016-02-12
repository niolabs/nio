"""
    NIO Command Holder class

"""
from nio.command.base import Command, InvalidCommandArg


class CommandHolder(object):

    """ Provides bookkeeping infrastructure surrounding block commands.

    """

    @classmethod
    def get_commands_entry(cls):
        """ Keeps the commands for the specific class where they
        are defined

        Returns:
            commands defined in the class
        """
        commands_attr = "{0}_commands_entry".format(cls.__name__)
        if not hasattr(cls, commands_attr):
            setattr(cls, commands_attr, {})
        return getattr(cls, commands_attr)

    @classmethod
    def get_commands(cls):
        """ Finds out all commands for the class, including commands for
        ancestor classes

        Once this method is called, it assumes no new command definitions
        are added to the class.

        Returns: all available commands for this class
        """
        commands_attr = "{0}_commands".format(cls.__name__)
        if not hasattr(cls, commands_attr):
            commands = dict()
            commands.update(cls.get_commands_entry())
            for _class in cls.__bases__:
                if issubclass(_class, CommandHolder):
                    commands.update(_class.get_commands())

            setattr(cls, commands_attr, commands)
        return getattr(cls, commands_attr)

    @classmethod
    def add_command(cls, command):
        """Commands are defined as instance methods on the block but
        are added to the block class as 'Command' objects for bookkeeping
        convenience and data encapsulation.

        Args:
            command (Command): A command object to be added.

        Returns:
            None

        """
        class_commands = cls.get_commands_entry()
        if isinstance(command, Command):
            class_commands[command.name] = command
        else:
            # TODO: log error
            pass

    @classmethod
    def get_command_description(cls):
        """ Determines the command descriptions for this class.
        This is useful in serialization/deserialization.

        Args:
            None

        Returns:
            description (dict): a dictionary containing both property and
                command data.

        """
        class_commands = cls.get_commands()
        commands = {}
        for c in class_commands:
            commands[c] = class_commands[c].get_description()
        return commands

    def invoke(self, name, args):
        """ Call the instance method 'name' with the specified arguments.

        Args:
            name (str): the name of the command/instance method
            args (dict{name: value}): the arguments to the command method.
                These will be assigned to the formal parameters of the
                command, being converted to the appropriate type in the process

        Returns:
            result: the return value of the command method

        """
        class_commands = self.get_commands()
        command = class_commands.get(name)
        if command is None or command.method is None:
            raise RuntimeError("Invalid command: %s" % name)

        method = getattr(self, command.method, None)

        if method is not None:
            args, kwargs = command.collect_arguments(args)
            try:
                result = method(*args, **kwargs)
            except TypeError as e:
                raise InvalidCommandArg(e)
        else:
            raise RuntimeError("Invalid command: %s" % name)

        return result
