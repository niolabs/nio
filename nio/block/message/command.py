class CommandMessage(object):

    """ Defines a command message to be sent from Block to Core
    """

    def __init__(self, service_name, block_name, command_name, command_args):
        """ Initializes the message

        Args:
            service_name (str): Service where command will be executed
            block_name (str): Block where command will be executed (optional,
                use empty or None to execute a Service command)
            command_name (str): Command to be executed
            command_args (dict): Command arguments with format
                {[arg_name]:[arg_value]}
        """
        self.service_name = service_name
        self.block_name = block_name
        self.command_name = command_name
        self.command_args = command_args

    def __str__(self):
        return "Command Message: " \
               "service name: {}, block name: {}, " \
               "command_name: {}, command_args: {}".\
            format(self.service_name, self.block_name,
                   self.command_name, self.command_args)
