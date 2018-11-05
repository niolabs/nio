from nio import discoverable
from nio.block.context import BlockContext
from nio.command import command
from nio.command.holder import CommandHolder
from nio.properties import PropertyHolder, VersionProperty, \
    BoolProperty, ListProperty, StringProperty, Property, SelectProperty
from nio.router.context import RouterContext
from nio.util.logging import get_nio_logger
from nio.util.logging.levels import LogLevel
from nio.util.flags_enum import FlagsEnum
from nio.util.runner import Runner, RunnerStatus
from nio.util.threading import spawn


class BlockException(Exception):

    """ Raised when a block fails to start, includes the block label.
    """
    def __init__(
            self, *args, block_label="Unknown block", block_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.block_label = block_label
        self.block_id = block_id


class BlockExecution(PropertyHolder):

    """ An object containing a block and its receivers

    Defines a single block execution within a potential execution graph
    A block execution is defined by a block name (name) and a set of block
    receivers where each receiver is identified by a block name.

    This information is parsed/used by the Router which is able then, based on
    the sending block, to forward signals to its receivers
    """
    id = StringProperty(title="Id")
    receivers = Property(title="Receivers")


class BlockMapping(PropertyHolder):

    """ An obejct containing a block and its alias in the service

    Allows a mapping of a given block based on another block
    This information is parsed/used internally by the core system
    """
    name = StringProperty(title="Name")
    mapping = StringProperty(title="Mapping")


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

    version = VersionProperty(version='1.0.0')
    type = StringProperty(title="Type", visible=False, readonly=True)
    id = StringProperty(title="Id", visible=False, allow_none=False)
    name = StringProperty(title="Name", allow_none=True)

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

        self._blocks_async_configure = None
        self._blocks_async_start = None
        self._blocks_async_stop = None

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
                try:
                    block.do_start()
                except Exception as e:
                    raise BlockException(
                        e, block_label=block.label(), block_id=block.id())

    def stop(self):
        """Overrideable method to be called when the service stops.

        If overriding, The service creator should call the stop method
        on the parent, after which it can assume that block router and blocks
        are stopped
        """
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
            # no apparent way to retrieve block label from the thread object
            threads.append({
                "block": block,
                "thread": spawn(getattr(block, method)),
            })

        for thread in threads:
            try:
                thread["thread"].join()
            except Exception as e:
                block = thread["block"]
                raise BlockException(
                    e, block_label=block.label(), block_id=block.id())

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
        self.logger = get_nio_logger(self.label())
        self.logger.setLevel(self.log_level())

        # instantiate block router
        self.logger.debug("Instantiating block router: {0}.{1}".
                          format(context.block_router_type.__module__,
                                 context.block_router_type.__name__))
        self.mgmt_signal_handler = context.mgmt_signal_handler
        self._blocks_async_configure = context.blocks_async_configure
        self._blocks_async_start = context.blocks_async_start
        self._blocks_async_stop = context.blocks_async_stop
        self._block_router = context.block_router_type()

        # create and configure blocks
        configure_threads = []
        for block_definition in context.blocks:
            block_context = self._create_block_context(
                block_definition['properties'],
                context)
            # create block instance
            block = block_definition['type']()
            # configure it
            if self._blocks_async_configure:
                # guarantee 'id' property is assigned to be able to reference
                # id() property down below
                block.id = block_context.properties["id"]
                configure_threads.append({
                    "block": block,
                    "thread": spawn(block.do_configure, block_context),
                })
            else:
                try:
                    block.do_configure(block_context)
                except Exception as e:
                    raise BlockException(
                        e, block_label=block.label(), block_id=block.id())
            # register it
            self._blocks[block.id()] = block
        # if configuration was async, ensure they are all done
        if configure_threads:
            for thread in configure_threads:
                try:
                    thread["thread"].join()
                except Exception as e:
                    block = thread["block"]
                    raise BlockException(
                        e, block_label=block.label(), block_id=block.id())

        # populate router context and configure block router
        router_context = RouterContext(self.execution(),
                                       self._blocks,
                                       context.router_settings,
                                       context.mgmt_signal_handler,
                                       context.instance_id,
                                       self.id(),
                                       self.name())
        self._block_router.do_configure(router_context)

    def _create_block_context(self, block_properties, service_context):
        """Populates block context to pass to the block's configure method"""
        return BlockContext(
            self._block_router,
            block_properties,
            service_context.properties.get('id'),
            service_context.properties.get('name', ""),
            self._create_commandable_url(service_context.properties,
                                         block_properties.get('id')),
            self.mgmt_signal_handler
        )

    def _create_commandable_url(self, service_properties, block_alias):
        """ Get the commandable url of a block given its alias """

        return '/services/{0}/{1}/'.format(
            service_properties.get('id', ''), block_alias)

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

        # build a general-like service status.
        service_and_blocks_status = FlagsEnum(RunnerStatus)
        # initialize it with the service status itself
        service_and_blocks_status.flags = self.status.flags
        # go trough its blocks and grab their warning and error statuses if any
        for block_id in self._blocks:
            if self._blocks[block_id].status.is_set(RunnerStatus.warning):
                service_and_blocks_status.add(RunnerStatus.warning)
            elif self._blocks[block_id].status.is_set(RunnerStatus.error):
                service_and_blocks_status.add(RunnerStatus.error)

        status = {"service": self.status.name,
                  "service_and_blocks": service_and_blocks_status.name,
                  "blocks": {}}
        # create a dict for all blocks using block label as key
        blocks = {}
        for block_id in self._blocks:
            block_status = {"status": self._blocks[block_id].status.name}
            if self._blocks[block_id].status.is_set(RunnerStatus.warning):
                block_status["warning"] = \
                    self._blocks[block_id]._messages[RunnerStatus.warning]
            if self._blocks[block_id].status.is_set(RunnerStatus.error):
                block_status["error"] = \
                    self._blocks[block_id]._messages[RunnerStatus.error]

            blocks[self._blocks[block_id].label()] = block_status

        status["blocks"] = blocks
        return status

    def label(self, include_id=False):
        """ Provides a label to a service based on name and id properties

        Args:
            include_id: whether id is to be included in label
        """
        if self.name():
            if include_id:
                return "{}-{}".format(self.name(), self.id())
            else:
                return self.name()
        return self.id()
