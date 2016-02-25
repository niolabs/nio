from nio.router.context import RouterContext
from nio.command import command
from nio.command.security import command_security
from nio.command.holder import CommandHolder
from nio import discoverable
from nio.util.versioning.dependency import DependsOn
from nio.properties import PropertyHolder, VersionProperty, \
    BoolProperty, ListProperty, StringProperty, VarProperty, SelectProperty
from nio.util.logging import get_nio_logger
from nio.util.logging.levels import LogLevel
from nio.modules.persistence import Persistence
from nio.modules.security.task import SecureTask
from nio.util.runner import Runner, RunnerStatus


class BlockExecution(PropertyHolder):

    """ Defines a single block execution within a potential execution graph
    A block execution is defined by a block name (name) and a set of block
    receivers where each receiver is identified by a block name.

    This information is parsed/used by the Router which is able then, based on
    the sending block, to forward signals to its receivers
    """
    name = StringProperty()
    receivers = VarProperty()


class BlockMapping(PropertyHolder):

    """ Allows a mapping of a given block based on another block
    This information is parsed/used internally by the core system
    """
    name = StringProperty()
    mapping = StringProperty()


@DependsOn("nio.modules.persistence", "1.0.0")
@DependsOn("nio.modules.scheduler", "1.0.0")
@DependsOn("nio.modules.security", "1.0.0")
@command('status', method="full_status")
@command('heartbeat')
@command('runproperties')
@command_security('start', SecureTask('services.start'))
@command_security('stop', SecureTask('services.stop'))
@discoverable
class Service(PropertyHolder, CommandHolder, Runner):

    """The base class for services.

    Once a service is created, the service is correctly executed
    by calling 'configure' and 'start'
    """

    version = VersionProperty(version='1.0.0')
    type = StringProperty(visible=False, readonly=True)
    name = StringProperty()

    # indicates whether service is to be started when nio starts
    auto_start = BoolProperty(default=False)
    # indicates the logging level
    log_level = SelectProperty(LogLevel, default="NOTSET")

    # properties defining the service execution
    execution = ListProperty(BlockExecution, default=[])
    mappings = ListProperty(BlockMapping, default=[])

    # System Metadata that can be used by API clients, which is serialized
    # along with any other service properties
    sys_metadata = StringProperty(visible=True, default="")

    def __init__(self, status_change_callback=None):
        """ Create a new service instance.

        Args:
            status_change_callback: method to call when status changes

        Take care of setting up instance variables in your service's
        constructor.
        """

        self._logger = get_nio_logger('service')
        super().__init__(status_change_callback=status_change_callback)

        # store service type so that it gets serialized
        self.type = self.__class__.__name__

        self._block_router = None
        self.mgmt_signal_handler = None
        self._blocks = {}
        self.mappings = []

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
            self._block_router.status.set(RunnerStatus.stopping)

        for block in self._blocks.values():
            block.do_stop()

        if self._block_router:
            self._block_router.do_stop()

    def configure(self, context):
        """Configure the service based on the context

        Args:
            context (ServiceContext): Specifies the information
                used to configure the service including service
                properties, block classes and properties for each
                block included in the service execution.
        """
        # populate service properties
        self.from_dict(context.properties, self._logger)

        # reset logger after modules initialization
        # and properties setting
        self._logger = get_nio_logger("service")
        self._logger.setLevel(self.log_level())

        # configure the Persistence module with the service name
        # TODO: unit test for the following
        # Persistence.configure(self.name)
        Persistence.configure(self.name())

        # instantiate block router
        self._logger.debug("Instantiating block router: {0}.{1}".
                           format(context.block_router_type.__module__,
                                  context.block_router_type.__name__))
        self._block_router = context.block_router_type()

        # create and configure blocks
        for block_definition in context.blocks:
            block_context = self._create_block_context(
                block_definition['type'],
                block_definition['properties'],
                context)
            block = self._create_and_configure_block(
                block_definition['type'],
                block_context)

            # TODO: write a unit test for this. they also pass with:
            # self._blocks[block.name] = block
            self._blocks[block.name()] = block

        # populate router context and configure block router
        router_context = RouterContext(self.execution(),
                                       self._blocks,
                                       context.router_settings,
                                       context.mgmt_signal_handler)
        self._block_router.do_configure(router_context)
        self.mgmt_signal_handler = context.mgmt_signal_handler

    def get_logger(self):
        """ Provides service logger
        """
        return self._logger

    def _create_block_context(self, block_type, block_properties,
                              service_context):
        """ Populates block context, which will serve as a basis
         for a future block configuration
        """

        from nio.block.context import BlockContext

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
        it exposes

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
        """ Returns service runtime properties
        """
        return self.to_dict()

    def full_status(self):
        """ Returns service plus block statuses for each block in the service
        """
        status = {"service": self.status.name}
        for name in self._blocks:
            status.update({name: self._blocks[name].status.name})
        return status
