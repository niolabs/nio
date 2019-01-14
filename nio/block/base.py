""" The base class for creating nio Blocks.

A block contains modular functionality to be used inside of Services. To create
a custom block, extend this Block class and override the appropriate methods.
"""
from collections import defaultdict

from nio.block.context import BlockContext
from nio.block.terminals import Terminal, TerminalType, input, output, \
    DEFAULT_TERMINAL
from nio.command import command
from nio.command.holder import CommandHolder
from nio.properties import PropertyHolder, StringProperty, \
    VersionProperty, SelectProperty
from nio.router.base import BlockRouter
from nio.signal.base import Signal
from nio.signal.status import BlockStatusSignal
from nio.util.logging import get_nio_logger
from nio.util.logging.levels import LogLevel
from nio.util.runner import Runner, RunnerStatus


@command('properties')
class Base(PropertyHolder, CommandHolder, Runner):

    """The base class for blocks to inherit from."""

    version = VersionProperty(version='0.0.0', advanced=True)
    type = StringProperty(title="Type", visible=False, readonly=True)
    id = StringProperty(title="Id", visible=False, allow_none=False)
    name = StringProperty(title="Name", visible=False, allow_none=True)
    log_level = SelectProperty(enum=LogLevel,
                               title="Log Level", default="NOTSET", advanced=True)

    def __init__(self, status_change_callback=None):
        """ Create a new block instance.

        Take care of setting up instance variables in your block's constructor.
        Note that the properties of the block are not available when the block
        is created. Those will be available when the block is configured.

        It is normally meaningless to pass variables to the constructor of the
        block. Any data the block requires will be passed through the
        BlockContext when the block is configured.
        """

        # We will replace the block's logger with its own name once we learn
        # what that name is during configure()
        self.logger = get_nio_logger('default')

        super().__init__(status_change_callback=status_change_callback)

        # store block type so that it gets serialized
        self.type = self.__class__.__name__

        self._block_router = None
        self._service_id = None
        self._service_name = None
        self._mgmt_signal_handler = None
        self._default_input = Terminal.get_default_terminal_on_class(
            self.__class__, TerminalType.input)
        self._default_output = Terminal.get_default_terminal_on_class(
            self.__class__, TerminalType.output)
        self._messages = defaultdict(str)

    def configure(self, context):
        """Overrideable method to be called when the block configures.

        The block creator should call the configure method on the parent,
        after which it can assume that any parent configuration options present
        on the block are loaded in as class variables. They can also assume
        that all functional modules in the service process are loaded and
        started.

        Args:
            context (BlockContext): The context to use to configure the block.

        Raises:
            TypeError: If the specified router is not a BlockRouter
        """
        if not isinstance(context, BlockContext):
            raise TypeError("Block must be configured with a BlockContext")
        # Ensure it is a BlockRouter so we can safely notify
        if not isinstance(context.block_router, BlockRouter):
            raise TypeError("Block's router must be instance of BlockRouter")

        self._block_router = context.block_router

        # load the configuration as class variables
        self.from_dict(context.properties, self.logger)
        # verify that block properties are valid
        self.validate()

        self.logger = get_nio_logger(self.label())
        self.logger.setLevel(self.log_level())
        self._service_id = context.service_id
        self._service_name = context.service_name
        self._mgmt_signal_handler = context.mgmt_signal_handler

    def start(self):
        """Overrideable method to be called when the block starts.

        The block creator can assume at this point that the block's
        initialization is complete and that the service and block router
        are in "starting" state.
        """
        pass  # pragma: no cover

    def stop(self):
        """Overrideable method to be called when the block stops.

        The block creator can assume at this point that the service and block
        router are in "stopping" state. All modules are still available for use
        in the service process.
        """
        pass  # pragma: no cover

    def set_status(self, status, message="", replace_existing=False):
        """ Set this block's status and notify the management channel.

        This is a method that a block developer can use to set their block's
        status. A block in warning or error status may be noted in the
        system designer or in monitoring tools.

        In general a block in warning status has a problematic condition but
        may be able to recover on its own (e.g., retrying a connection). A
        block in error status is in a state that will require a human to
        resolve the error; either by fixing the error condition or restarting
        the service.

        Args:
            status (str or RunnerStatus): A nio.util.runner.RunnerStatus to
                set the block's statut to. Optionally takes a string if the
                string is one of (error, warning, ok). Specifying 'error' or
                'warning' will set those status flags on the block. Specifying
                any non-error status as a status will clear both any error or
                warning status flags on the block.
            message (str): An optional string message to include in the
                notification of the status change.
            replace_existing (bool): Whether or not to replace the existing
                block status when setting the new status. If False, the new
                status will be added to the block if it is a warning or error
                status. Any non-error/warning status will clear any error or
                warning status that was on the block before.

        Returns:
            RunnerStatus: The current block's status after setting.

        Raises:
            ValueError: If a string other than "ok", "warning", or "error" is
                provided as the status
            TypeError: If an invalid status type or message type is specified
        """
        if isinstance(status, str):
            if status.lower() == 'ok':
                # An ok status means we want the first non-error status that
                # is on the block right now.
                # Default to a created status if the block has no statues left
                status = RunnerStatus.created
                for flag, flag_set in self.status.flags.items():
                    if flag in ('warning', 'error'):
                        continue
                    if flag_set:
                        status = RunnerStatus[flag]
                        break
            elif status.lower() == 'warn' or status.lower() == 'warning':
                status = RunnerStatus.warning
            elif status.lower() == 'error':
                status = RunnerStatus.error
            else:
                raise ValueError("Only 'ok', 'warning', or 'error' are "
                                 "supported status strings")
        elif not isinstance(status, RunnerStatus):
            raise TypeError(
                "Block status can only be set to string or RunnerStatus")

        if not isinstance(message, str):
            raise TypeError("Only string based status messages are allowed")

        # Clear old error/warn status if a non-error/warn status is passed
        if status != RunnerStatus.error:
            self.status.remove(RunnerStatus.error)
            if RunnerStatus.error in self._messages:
                del self._messages[RunnerStatus.error]
        else:
            self._messages[RunnerStatus.error] = message

        if status != RunnerStatus.warning:
            self.status.remove(RunnerStatus.warning)
            if RunnerStatus.warning in self._messages:
                del self._messages[RunnerStatus.warning]
        else:
            self._messages[RunnerStatus.warning] = message

        if replace_existing:
            self.status.set(status)
        else:
            self.status.add(status)

        # Notify the new status to the management channel for other services
        # to handle
        signal = BlockStatusSignal(status, message=message)
        self.notify_management_signal(signal)
        return self.status

    def notify_signals(self, signals, output_id=None):
        """Notify signals to router.

        This is the method the block should call whenever it would like
        to "output" signals for the router to send downstream. Empty signal
        lists are safely/silently ignored.

        Args:
            signals (list): A list of signals to notify to the router
            output_id: The identifier of the output terminal to notify the
                signals on

        The signals argument is handled as follows:
            - a dictionary is not allowed
            - if a single signal is notified not as an iterable, it will get
            wrapped inside a list before forwarding to block router.

        Raises:
            TypeError: when signals are not instances of class Signal
        """
        if isinstance(signals, dict):
            raise TypeError("Signals cannot be a dictionary")

        if not signals:
            self.logger.debug("Ignoring empty signal list")
            return

        # if a single Signal is being notified, make it a list
        if isinstance(signals, Signal):
            signals = [signals]

        self._block_router.notify_signals(self, signals, output_id)

    def notify_management_signal(self, signal):
        """Notify a management signal to router.

        Args:
            signal: signal to notify

        This is a special type of signal notification that does not actually
        propagate signals in the service. Instead, it is used to communicate
        some information to the block router about the block. For example,
        the block can report itself in an error state and thus prevent other
        signals from being delivered to it.
        """
        if self._mgmt_signal_handler:
            if isinstance(signal, BlockStatusSignal):
                # add service and block info
                signal.service_id = self._service_id
                signal.service_name = self._service_name
                signal.block_id = self.id()
                signal.block_name = self.name()
            self._mgmt_signal_handler(signal)

    def process_signals(self, signals, input_id=DEFAULT_TERMINAL):
        """Overrideable method to be called when signals are delivered.

        This method will be called by the block router whenever signals
        are sent to the block. The method should not return the modified
        signals, but rather call `notify_signals` so that the router
        can route them properly.

        Args:
            signals (list): A list of signals to be processed by the block
            input_id: The identifier of the input terminal the signals are
                being delivered to
        """
        pass  # pragma: no cover

    @classmethod
    def get_description(cls):
        """ Get a dictionary description of this block.

        Returns:
            dict: A dictionary containing the blocks properties and commands
        """
        properties = super().get_description()
        commands = cls.get_command_description()

        return {
            'properties': properties,
            'commands': commands
        }

    def properties(self):
        """ Returns block runtime properties """
        return self.to_dict()

    @classmethod
    def inputs(cls):
        """ A list of the block's input terminals """
        return Terminal.get_terminals_on_class(cls, TerminalType.input)

    @classmethod
    def outputs(cls):
        """ A list of the block's output terminals """
        return Terminal.get_terminals_on_class(cls, TerminalType.output)

    def is_input_valid(self, input_id):
        """ Find out if input is valid

        Args:
            input_id: input identifier

        Returns:
            bool: True if the input ID exists on this block
        """
        return input_id in [i.id for i in self.__class__.inputs()]

    def is_output_valid(self, output_id):
        """ Find out if output is valid

        Args:
            output_id: output identifier

        Returns:
            bool: True if the output ID exists on this block
        """
        return output_id in [o.id for o in self.__class__.outputs()]

    def label(self, include_id=False):
        """ Provides a label to a block based on name and id properties

        Args:
            include_id: whether id is to be included in label
        """
        if self.name():
            if include_id:
                return "{}-{}".format(self.name(), self.id())
            else:
                return self.name()
        return self.id()


@input(DEFAULT_TERMINAL, default=True, label="default")
@output(DEFAULT_TERMINAL, default=True, label="default")
class Block(Base):
    pass
