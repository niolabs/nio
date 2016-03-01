"""

   Service Context: The data that a service will be configured with

"""


class ServiceContext(object):

    def __init__(self, properties, blocks=None,
                 block_router_type=None, router_settings=None,
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
        self.mgmt_signal_handler = mgmt_signal_handler
