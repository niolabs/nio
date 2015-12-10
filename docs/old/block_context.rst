Block Context
-------------

In the configure method, blocks are passed 'context' about themselves and the environment that they are running in. This information is available to be used by block developers:

*  block_router (BlockRouter):The router in which the block will be running. The only requirements are that it can handle signals notified by its blocks.
*  properties (dict): The block properties (metadata) that will be deserialized and loaded as block properties.
*  hooks (Hooks): Hooks to subscribe to participate in the lifecycle process involving all blocks running together.
*  service_name (str): The name of the service this block belongs to.
*  command_url (str): The URL at which this block can be commanded. This URL will not have host or port information, as that may be different based on public/private IP. It will look like "/services/ServiceName/BlockAlias/".
*  mgmt_signal_handler (method): method to use to publish management signals
