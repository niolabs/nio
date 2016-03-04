"""
    NIO Command Holder class

"""
from nio.command.base import Command, InvalidCommandArg


class CommandHolder(object):

    @classmethod
    def get_commands_entry(cls):
        """Get all commands on this CommandHolder.

        This does not include commands defined on parent classes.

        Returns:
            dict: commands defined in the class

        """
        commands_attr = "{0}_commands_entry".format(cls.__name__)
        if not hasattr(cls, commands_attr):
            setattr(cls, commands_attr, {})
        return getattr(cls, commands_attr)

    @classmethod
    def get_commands(cls):
        """Get all commands on this CommandHolder and its parent classes.

        This does include commands defined on parent classes.

        Once this method is called, it assumes no new command definitions
        are added to the class.

        Returns:
            dict: all available commands for this class

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
        """Add a command to this CommandHolder.

        Commands are defined as instance methods on the block but
        are added to the block class as 'Command' objects for bookkeeping
        convenience and data encapsulation.

        Args:
            command (Command): A command object to be added.

        """
        class_commands = cls.get_commands_entry()
        if isinstance(command, Command):
            class_commands[command.name] = command
        else:
            raise TypeError("Added command must be an instance of Command")

    @classmethod
    def get_command_description(cls):
        """Get the command descriptions for this CommandHolder and its parents.

        This is useful in serialization/deserialization.

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
            raise RuntimeError("Invalid command: {}".format(name))

        method = getattr(self, command.method, None)

        if method is not None:
            args, kwargs = command.collect_arguments(args)
            try:
                result = method(*args, **kwargs)
            except TypeError as e:
                raise InvalidCommandArg(e)
        else:
            raise RuntimeError("Invalid command: {}".format(name))

        return result
