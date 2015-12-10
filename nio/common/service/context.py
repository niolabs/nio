"""

   Service Init Context

"""


class ServiceContext(object):

    def __init__(self, service_type, properties,
                 ipc_class, service_pipe, core_pipe,
                 blocks=None, block_router_type=None, module_config=None,
                 modules=None, root='', module_locations=None,
                 identity_info=None, router_settings=None):
        """ Initializes information needed for a Service

        Arguments:
            service_type (class type): service class type
            properties (dict): service metadata
            ipc_class: class to instantiate for InterProcessCommunications
            service_pipe (python pipe): service pipe for ipc communication
            core_pipe (python pipe): core pipe for ipc communication
            blocks (list): list of blocks, each with the format:
                {"type": block class,
                 "properties": block metadata}
            block_router_type: block router class to use
            module_config (Configuration): Additional configuration specific
                to the service. The values here will replace default module
                configuration values.
            modules: module names to initialize, this list is populated by
                builders and context preparers, however, just before launching
                service, this is transformed into a list of
                (module name, module class)
            root (str): path to working directory (project root)
            identity_info (dict): contains originating identity information
                such as: ip address, port, instance_name,
                source (service name or 'main')
            router_settings (dict): router settings, , these can include
                "clone_signals" and/or any other settings depending on router
                being used
        """
        self.service_type = service_type
        self.properties = properties
        self.ipc_class = ipc_class
        self.service_pipe = service_pipe
        self.core_pipe = core_pipe
        self.blocks = blocks if blocks is not None else {}
        self.block_router_type = block_router_type
        self.module_config = module_config if module_config is not None else {}
        self.modules = list(modules) if modules is not None else []
        self.module_locations = module_locations
        self.root = root
        self.identity_info = identity_info
        self.router_settings = router_settings or {}

        # data core components write to for service
        self.service_data = {}
        # data core components write to for all blocks
        self.all_blocks_data = {}
        # data core components write to for specific blocks
        self.block_data = {}

    def get_service_data(self):
        """ Allows to retrieve data saved for the service by core components
        """
        return self.service_data

    def get_block_data(self, block_type=None):
        """ Allows to retrieve data saved for the block by core components

        Arguments:
            block_type (string): if None, all blocks data set by core
                components is retrieved, otherwise data is retrieved for
                the specified block_type, where block_type is a string
                containing the block namespace
        """
        if block_type:
            return self.block_data.get(block_type)
        return self.all_blocks_data
