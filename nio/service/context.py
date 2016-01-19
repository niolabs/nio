"""

   Service Context: The data that a service will be configured with

"""


class ServiceContext(object):

    def __init__(self, properties, blocks=None,
                 block_router_type=None, router_settings=None,
                 service_data=None, block_data=None, all_blocks_data=None,
                 mgmt_signal_handler=None):
        """ Initializes information needed for a Service

        Arguments:
            properties (dict): service metadata
            blocks (list): list of blocks, each with the format:
                {"type": block class,
                 "properties": block metadata}
            block_router_type: block router class to use
            router_settings (dict): router settings, , these can include
                "clone_signals" and/or any other settings depending on router
                being used
            mgmt_signal_handler (method): method to use to publish
                management signals, receives signal as only parameter
        """
        self.properties = properties
        self.blocks = blocks if blocks is not None else {}
        self.block_router_type = block_router_type
        self.router_settings = router_settings or {}

        # data core components write to for service
        self.service_data = service_data or {}
        # data core components write to for all blocks
        self.all_blocks_data = all_blocks_data or {}
        # data core components write to for specific blocks
        self.block_data = block_data or {}
        self.mgmt_signal_handler = mgmt_signal_handler

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
