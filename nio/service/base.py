from nio import discoverable
from nio.block.context import BlockContext
from nio.command import command
from nio.command.holder import CommandHolder
from nio.properties import PropertyHolder, VersionProperty, \
    BoolProperty, ListProperty, StringProperty, Property, SelectProperty
from nio.properties.util.safe_eval import SafeEval
from nio.router.context import RouterContext
from nio.util.logging import get_nio_logger
from nio.util.logging.levels import LogLevel
from nio.util.runner import Runner, RunnerStatus
from nio.util.threading import spawn
from nio.util.versioning.dependency import DependsOn


class BlockExecution(PropertyHolder):

    """ An object containing a block and its receivers

    Defines a single block execution within a potential execution graph
    A block execution is defined by a block name (name) and a set of block
    receivers where each receiver is identified by a block name.

    This information is parsed/used by the Router which is able then, based on
    the sending block, to forward signals to its receivers
    """
    name = StringProperty(title="Name")
    receivers = Property(title="Receivers")


class BlockMapping(PropertyHolder):

    """ An obejct containing a block and its alias in the service

    Allows a mapping of a given block based on another block
    This information is parsed/used internally by the core system
    """
    name = StringProperty(title="Name")
    mapping = StringProperty(title="Mapping")


@DependsOn("nio", "2.0.0b1")
@command('status', method="full_status")
@command('heartbeat')
@command('runproperties')
@command('start')
@command('stop')
@discoverable
class Service(PropertyHolder, CommandHolder, Runner):

    """The base class for services.

    Once a service is created, the service is correctly executed
    by calling 'configure' and 'start'
    """

    version = VersionProperty(version='0.1.0')
    type = StringProperty(title="Type", visible=False, readonly=True)
    name = StringProperty(title="Name")

    # indicates whether service is to be started when nio starts
    auto_start = BoolProperty(title="Auto Start", default=True)
    # indicates the logging level
    log_level = SelectProperty(LogLevel, title="Log Level", default="NOTSET")

    # properties defining the service execution
    execution = ListProperty(BlockExecution, title="Execution", default=[])
    mappings = ListProperty(BlockMapping, title="Mappings", default=[])

    # System Metadata that can be used by API clients, which is serialized
    # along with any other service properties
    sys_metadata = StringProperty(title="Metadata", visible=True, default="")

    def __init__(self, status_change_callback=None):
        """ Create a new service instance.

        Args:
            status_change_callback: method to call when status changes

        Take care of setting up instance variables in your service's
        constructor.
        """

        self.logger = get_nio_logger('service')
        super().__init__(status_change_callback=status_change_callback)

        # store service type so that it gets serialized
        self.type = self.__class__.__name__

        self._block_router = None
        self.mgmt_signal_handler = None
        self._blocks = {}
        self.mappings = []

        self._blocks_async_start = False
        self._blocks_async_stop = True

    def start(self):
        """Overrideable method to be called when the service starts.

        The service creator can assume at this point that the service's
        configuration is complete.

        If overriding, The service creator should call the start method
        on the parent, after which it can assume that block router and blocks
        are started
        """
        if self._block_router:
            self._block_router.do_start()

        if self._blocks_async_start:
            self._execute_on_blocks_async("do_start")
        else:
            for block in self._blocks.values():
                block.do_start()

    def stop(self):
        """Overrideable method to be called when the service stops.

        If overriding, The service creator should call the stop method
        on the parent, after which it can assume that block router and blocks
        are stopped
        """
        if self._block_router:
            # 'alert' block controller that service will be
            # 'stopped' shortly
            self._block_router.status = RunnerStatus.stopping

        if self._blocks_async_stop:
            self._execute_on_blocks_async("do_stop")
        else:
            for block in self._blocks.values():
                block.do_stop()

        if self._block_router:
            self._block_router.do_stop()

    def _execute_on_blocks_async(self, method):
        """ Performs given method on all blocks in an async manner

        A join operation is performed for each spawned thread, that way we
        can assure that each block gets a chance to execute fully before
        leaving this method.

        Since created threads are not exposed to caller, and there is a
        potential for a spawned thread to be non-responsive, it is recommended
        that this or a method in the stack hierarchy leading to this method be
        spawned itself.

        Args:
            method (str): method to execute on blocks

        """
        threads = []
        for block in self._blocks.values():
            threads.append(spawn(getattr(block, method)))

        for thread in threads:
            thread.join()

    def configure(self, context):
        """Configure the service based on the context

        Args:
            context (ServiceContext): Specifies the information
                used to configure the service including service
                properties, block classes and properties for each
                block included in the service execution.
        """
        # populate service properties
        self.from_dict(context.properties, self.logger)
        # verify that service properties are valid
        self.validate()

        # reset logger after modules initialization
        # and properties setting
        self.logger = get_nio_logger("service")
        self.logger.setLevel(self.log_level())

        # instantiate block router
        self.logger.debug("Instantiating block router: {0}.{1}".
                          format(context.block_router_type.__module__,
                                 context.block_router_type.__name__))
        self._block_router = context.block_router_type()

        # create and configure blocks
        for block_definition in context.blocks:
            block_context = self._create_block_context(
                block_definition['properties'],
                context)
            block = self._create_and_configure_block(
                block_definition['type'],
                block_context)
            self._blocks[block.name()] = block

        # populate router context and configure block router
        router_context = RouterContext(self.execution(),
                                       self._blocks,
                                       context.router_settings,
                                       context.mgmt_signal_handler)
        self._block_router.do_configure(router_context)
        self.mgmt_signal_handler = context.mgmt_signal_handler
        self._blocks_async_start = context.blocks_async_start
        self._blocks_async_stop = context.blocks_async_stop
        if context.eval_modules:
            SafeEval.set_modules(context.eval_modules)

    def _create_block_context(self, block_properties, service_context):
        """Populates block context to pass to the block's configure method"""
        return BlockContext(
            self._block_router,
            block_properties,
            service_context.properties.get('name', ''),
            self._create_commandable_url(service_context.properties,
                                         block_properties.get('name', ''))
        )

    def _create_commandable_url(self, service_properties, block_alias):
        """ Get the commandable url of a block given its alias """

        return '/services/{0}/{1}/'.format(
            service_properties.get('name', ''), block_alias)

    def _create_and_configure_block(self, block_type, block_context):
        """ Instantiates and configures given block """
        block = block_type()
        block.do_configure(block_context)
        return block

    @classmethod
    def get_description(cls):
        """ Retrieves a service description based on properties and commands

        Returns:
            Service description
        """
        properties = super().get_description()
        commands = cls.get_command_description()
        return {'properties': properties,
                'commands': commands}

    @property
    def blocks(self):
        """ Allow access to service blocks """
        return self._blocks

    def heartbeat(self):
        """ Allows monitoring

        Returns:
            Service status
        """
        return self.status

    def runproperties(self):
        """ Returns service runtime properties """
        return self.to_dict()

    def full_status(self):
        """Returns service plus block statuses for each block in the service"""
        status = {"service": self.status.name}
        for name in self._blocks:
            status.update({name: self._blocks[name].status.name})
        return status
