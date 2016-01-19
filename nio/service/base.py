from nio.common import ComponentStatus
from nio.router.base import RouterStatus
from nio.router.context import RouterContext
from nio.common.command import command
from nio.common.command.security import command_security
from nio.common.command.holder import CommandHolder
from nio import discoverable
from nio.common.versioning.dependency import DependsOn
from nio.metadata.properties import PropertyHolder, VersionProperty, \
    BoolProperty, ListProperty, StringProperty, VarProperty, SelectProperty
from nio.util.logging import get_nio_logger
from nio.util.logging.levels import LogLevel
from nio.modules.persistence import Persistence
from nio.modules.security.permissions.authorizer import has_permission
from nio.util.flags_enum import FlagsEnum


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
@command_security('start', True, has_permission('services.start'))
@command_security('stop', True, has_permission('services.stop'))
@discoverable
class Service(PropertyHolder, CommandHolder):

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
    execution = ListProperty(BlockExecution)
    mappings = ListProperty(BlockMapping)

    # System Metadata that can be used by API clients, which is serialized
    # along with any other service properties
    sys_metadata = StringProperty(visible=True, default="")

    def __init__(self):
        """ Create a new service instance.

        Take care of setting up instance variables in your service's
        constructor.
        """

        super().__init__()

        # store service type so that it gets serialized
        self.type = self.__class__.__name__

        self._logger = get_nio_logger('service')
        self._block_router = None
        self._blocks = {}
        self.mappings = []
        self._status = FlagsEnum(ComponentStatus)
        self._status.set(ComponentStatus.created)

    def start(self):
        """ Starts the service.

        Starting a service comprises tasks such as:
            Starting the block router
            Starting each service block

        """
        self.status.set(ComponentStatus.starting)
        try:
            self.on_start()
            self.status.set(ComponentStatus.started)
        except Exception:
            self._logger.exception("Failed to start service")
            self.status.add(ComponentStatus.error)
            raise

    def stop(self):
        """ Stops the service.

        Stopping a service comprises tasks such as:
            Stopping each service block
            Stopping the block router

        """
        self.status.set(ComponentStatus.stopping)
        self.on_stop()
        # This change in status creates an error trying to use the log
        # when the logging module was already finalized
        self.status.set(ComponentStatus.stopped)

    def configure(self, context):
        """ Configures the service based on the context, the context
        will contain configuration information serving to configuring
        the service and its blocks.

        Configuring a service comprises tasks such as:
            Setting the service properties
            Creating and configuring the block router
            Creating and configuring each service block

        Args:
            context (ServiceContext): Specifies the information
                used to configure the service including service
                properties, block classes and properties for each
                block included in the service execution.
        """
        self.status.set(ComponentStatus.configuring)
        try:
            self.on_configure(context)
            self.status.set(ComponentStatus.configured)
        except Exception:
            self._logger.exception("Failed to configure service")
            self.status.add(ComponentStatus.error)
            raise

    def on_start(self):
        """Overrideable method to be called when the service starts.

        The service creator can assume at this point that the service's
        configuration is complete.

        If overriding, The service creator should call the on_start method
        on the parent, after which it can assume that block router and blocks
        are started
        """
        if self._block_router:
            self._block_router.start()

        for block in self._blocks.values():
            try:
                block.status.set(ComponentStatus.starting)
                block.start()
                block.status.set(ComponentStatus.started)
            except Exception:
                self._logger.exception(
                    "Block: {0} failed to start".format(block.name))
                raise

    def on_stop(self):
        """Overrideable method to be called when the service stops.

        If overriding, The service creator should call the on_stop method
        on the parent, after which it can assume that block router and blocks
        are stopped
        """
        if self._block_router:
            # 'alert' block controller that service will be
            # 'stopped' shortly
            self._block_router.status.set(RouterStatus.stopping)

        for block in self._blocks.values():
            block.status.set(ComponentStatus.stopping)
            block.stop()
            block.status.set(ComponentStatus.stopped)

        if self._block_router:
            self._block_router.stop()

    def on_configure(self, context):
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
        self._logger.setLevel(self.log_level)

        # configure the Persistence module with the service name
        Persistence.configure(self.name)

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

            self._blocks[block.name] = block

        # populate router context and configure block router
        router_context = RouterContext(self.execution,
                                       self._blocks,
                                       context.router_settings)
        self._block_router.configure(router_context)

    @property
    def status(self):
        """ Provides service status
        """
        return self._status

    def _create_block_context(self, block_type, block_properties,
                              service_context):
        """ Populates block context, which will serve as a basis
         for a future block configuration
        """

        # populate component data member for given block by getting
        # data for all blocks and merging it with specific block data
        component_data = service_context.get_block_data()
        # TODO: Do we need to merge in individual block data here? Why were
        # we doing that before?

        from nio.block.context import BlockContext

        return BlockContext(
            self._block_router,
            block_properties,
            component_data,
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
        try:
            block.status.set(ComponentStatus.configuring)
            block.configure(block_context)
            block.status.set(ComponentStatus.configured)
        except Exception:
            self._logger.exception(
                "Block: {0} failed to configure".format(block.name))
            raise
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
