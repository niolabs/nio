from nio.common.command import command
from nio.common.command.holder import CommandHolder
from nio.common.block.router import BlockRouter
from nio.metadata.properties import PropertyHolder, StringProperty, \
    VersionProperty, SelectProperty
from nio.util.logging import get_nio_logger
from nio.util.logging.levels import LogLevel
from nio.modules.persistence import Persistence
from nio.block.terminals import Terminal, TerminalType, Input, Output


@Input("default")
@Output("default")
@command('properties')
class Block(PropertyHolder, CommandHolder):

    """The base class for blocks to inherit from.

    Once a block is created, at some point before starting the block
    the `configure` method should be called, indicating who the block's
    parent is and what configuration it has.
    """

    version = VersionProperty(version='0.0.0')
    type = StringProperty(visible=False, readonly=True)
    name = StringProperty(visible=False)
    log_level = SelectProperty(LogLevel, title="Log Level", default="NOTSET")

    def __init__(self):
        """ Initializes block variables.

        Args:
            None

        Returns:
            None

        """

        # store block type so that it gets serialized
        self.type = self.__class__.__name__

        self._block_router = None
        self._logger = get_nio_logger('default')
        self.persistence = None

    def start(self):
        """The overrideable method to be called when the block's parent
        controller is started.

        The block creator can assume at this point that the block's
        initialization is complete and that the service or parent controller
        is in "starting" state.
        """
        pass

    def stop(self):
        """The overrideable method to be called when the block's parent
        controller is stopped.

        The block creator can assume at this point that the service or
        parent controller is in "stopping" state. All functional modules are
        still available for use in the service process.
        """
        pass

    def configure(self, context):
        """Configure method to override when subclassing block

        The block creator should call the configure method on the parent,
        after which it can assume that any parent configuration options present
        on the block are loaded in as class variables. They can also assume
        that all functional modules in the service process are loaded and
        started.

        Args:
            context (ServiceContext (block): The context to use to configure
            the block.

        Raises:
            TypeError: If the specified router is not a BlockRouter
        """
        # Ensure it is a BlockRouter so we can safely notify
        if not isinstance(context.block_router, BlockRouter):
            raise TypeError("Block's router must be instance of BlockRouter")

        self._block_router = context.block_router

        # load the configuration as class variables
        self.from_dict(context.properties, self._logger)

        self._logger = get_nio_logger(self.name)
        self._logger.setLevel(self.log_level)

        self.persistence = Persistence(self.name)

    def notify_signals(self, signals, output_id='default'):
        """Notify signals to router.

        This is the method the block should call whenever it would like
        to "output" signals for the router to send downstream.

        Args:
            signals (list): A list of signals to notify to the router
            output_id: output identifier
        """
        self._block_router.notify_signals(self, signals, output_id)

    def notify_management_signal(self, signal):
        self._block_router.notify_management_signal(self, signal)

    def process_signals(self, signals, input_id='default'):
        """The overrideable method to be called when signals are sent to the
        block from the block's router.

        This method will be called by the parent context whenever signals
        are sent to the block. The method should not return the modified
        signals, but rather call `notify_signals` so that the router
        can route them properly.

        Args:
            signals (list): A list of signals to be processed by the block
            input_id: input identifier
        """
        pass  # pragma: no cover

    @classmethod
    def get_description(cls):
        properties = super().get_description()
        commands = cls.get_command_description()

        return {'properties': properties,
                'commands': commands}

    def properties(self):
        """ Returns block runtime properties
        """
        return self.to_dict()

    @property
    def inputs(self):
        return list(Terminal.get_terminals_on_class(
            self.__class__, TerminalType.input))

    @property
    def outputs(self):
        return list(Terminal.get_terminals_on_class(
            self.__class__, TerminalType.output))

    def is_input_valid(self, input_id):
        """ Find out if input is valid

        Args:
            input_id: input identifier
        """
        return input_id in self.inputs

    def is_output_valid(self, output_id):
        """ Find out if output is valid

        Args:
            output_id: input identifier
        """
        return output_id in self.outputs
