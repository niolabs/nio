""" The data that a block will be configured with """


class BlockContext(object):

    def __init__(self, block_router, properties, component_data,
                 service_name='', command_url=''):
        """ Initializes information needed for a Block

        This BlockContext will be passed to the `configure` method on each
        block instance before getting started.

        Args:
            block_router (BlockRouter): The router in which the
                block will be running. The only requirements are that it
                can handle signals notified by its blocks.

            properties (dict): The block properties (metadata) that
                will be deserialized and loaded as block properties.
            component_data (dict): data set by components
            service_name (str): The name of the service this block belongs to
            command_url (str): The URL at which this block can be commanded.
                This URL will not have host or port information, as that may
                be different based on public/private IP. It will look like
                "/services/ServiceName/BlockAlias/"

        """

        self.block_router = block_router
        self.properties = properties
        self.component_data = component_data
        self.service_name = service_name
        self.command_url = command_url
