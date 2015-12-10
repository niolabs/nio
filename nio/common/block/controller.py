from enum import Enum
import inspect

from nio.common.block.router import BlockRouter
from nio.util.logging import get_nio_logger
from nio.common.signal.management import ManagementSignal
from nio.common.signal.status import BlockStatusSignal


class BlockState(Enum):
    creating = 1
    created = 2
    configuring = 3
    configured = 4
    stopping = 5
    stopped = 6
    starting = 7
    started = 8


class BlockStatus(Enum):
    ok = 1
    warning = 2
    error = 3


class InvalidProcessSignalsSignature(Exception):
    pass


class BlockController(BlockRouter):
    """The block controller class.

    This class is meant to sit in the middle of the actual block and the
    actual block router.

    To blocks, it will look like a BlockRouter. Blocks will get configured
    with an instance of this class as their block router, and they can call
    notify_signals on this class. It extends from BlockRouter so that the
    underlying block can check the type.

    To BlockRouters, it will look like a Block. When routing, a block router
    can call process_signals on this instance as if it were the actual block.
    The controller will take care of making sure the underlying block is
    ready to receive those signals.

    This class will also make decisions when sending signals to the
    block depending on the block status and state when delivering signals
    or sending commands to the block.

    """

    def __init__(self, block_type):
        """ Initializes block controller's variables.

        Args:
            block_type (class): The type of block that will be created.
        """
        super().__init__()

        self._block_type = block_type

        # This variable will ultimately contain the underlying block
        self._block = None

        # initialize service name
        self._service_name = None

        self._status = BlockStatus.ok
        self._state = BlockState.creating

        # This variable will ultimately contain the actual block router that
        # this controller acts as
        self._block_router = None
        self._logger = get_nio_logger('default')
        self._mgmt_signal_handler = self._default_mgmt_signal_handler

        self._pass_input_id = True

    def start(self):
        """Start the component.

        This method will update the state and call the block start method.
        """
        self.state = BlockState.starting
        self._block.start()
        self.state = BlockState.started

    def stop(self):
        """Stop the component.

        This method will update the state and call the block stop method.
        """
        self.state = BlockState.stopping
        self._block.stop()
        self.state = BlockState.stopped

    def configure(self, context):
        """Configures the block based on information passed in the context.

        Args:
            context (ServiceContext (block)): The context to use to configure
            block being controlled.
        """
        self._block = self._block_type()

        self._service_name = context.service_name

        self.state = BlockState.created

        # Put this instance in between the block and the block router by saving
        # the original block router. Then update the context that will be
        # delivered to the block to have this instance as its block router.
        self._block_router = context.block_router
        context.block_router = self
        # override management signal handler
        self._mgmt_signal_handler = context.mgmt_signal_handler

        # Now configure the actual block
        self.state = BlockState.configuring
        self._block.configure(context)

        self._logger = get_nio_logger(self.name)

        # config_name will have the "originating" block name
        self._block.config_name = self._block.name

        self.state = BlockState.configured

        # determine underlying block support
        self._pass_input_id = self._supports_input_id()

    def invoke(self, command, args):
        """ Intermediate method to pass a command and its arguments
        along to a block.

        Args:
            command (str): The name of the command.
            args (dict): Of the form {param_name: value}

        Returns:
            The result of the command invocation

        """
        return self._block.invoke(command, args)

    def notify_signals(self, block, signals, output_id):
        """Notify signals to router.

        This is the method the block should call whenever it would like
        to "output" signals for the router to send downstream.

        Args:
            block (Block): The block that is notifying
            signals (list): A list of signals to notify to the router
            output_id: output identifier
        """
        self._block_router.notify_signals(self, signals, output_id)

    def notify_management_signal(self, block, signal):
        """Notify management signals to router.

        This is called, for example, when a block changes status at runtime.

        Args:
            block (Block): The block that is notifying.
            signal (ManagementSignal): The management signal to notify to
                the router.

        Return:
            None

        """
        if isinstance(signal, ManagementSignal):
            if isinstance(signal, BlockStatusSignal):
                # set service block is part of
                signal.service_name = self._service_name
                signal.name = block.name
                self.status = signal.status
                self._logger.debug("Block status change: %s" % signal.msg)
            # publish it through system
            self._mgmt_signal_handler([signal])
        else:
            self._logger.error("%s detected in BlockController."
                               "notify_management_signal()" % type(signal))

    def _default_mgmt_signal_handler(self, signals):
        pass

    def process_signals(self, signals, input_id='default'):
        """This method is called from the router to send signals to a block.

        Args:
            signals (list): A list of signals to be processed by the block
        """
        if self._pass_input_id:
            self._block.process_signals(signals, input_id)
        else:
            self._block.process_signals(signals)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        """ Block Status

        Possible values are based on BlockStatus

        """
        self._logger.info("Block: {} (type: {}) status is {}".format(
            self._block.name, self._block.__class__.__name__, status.name))
        self._status = status

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        """ Block State

        Possible values are based on BlockState

        """
        self._logger.info("Block: {} (type: {}) status is {}".format(
            self._block.name, self._block.__class__.__name__, state.name))
        self._state = state

    @property
    def name(self):
        return self._block.name

    @name.setter
    def name(self, name):
        """ name is same as Block Name for controller to use

        """
        self._block.name = name

    @property
    def block(self):
        return self._block

    def _supports_input_id(self):
        """ Finds out if instantiated block's signature is of newer type
        (self, signals, input_id)

        Args:
            block: Instantiated service block
        """

        # determine 'process_signals' signature details
        args_spec = inspect.getargspec(self._block.process_signals)
        if len(args_spec.args) == 2:
            # method signature assumed to be (self, signals)
            # ==> disregard input_id even when present
            return False
        elif len(args_spec.args) == 3:
            # method signature assumed to be (self, signals, input_id)
            return True
        else:
            raise InvalidProcessSignalsSignature(
                "Block {0} signature is invalid".format(self._block.name))

    @property
    def inputs(self):
        return self._block.inputs

    def is_input_valid(self, input_id):
        return self._block.is_input_valid(input_id)

    def is_output_valid(self, output_id):
        return self._block.is_output_valid(output_id)
