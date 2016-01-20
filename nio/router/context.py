class RouterContext(object):

    """ Maintains information needed to configure a block router """

    def __init__(self, execution, blocks, settings=None,
                 mgmt_signal_handler=None):
        """Initializes a router context.

        Args:
            execution (list):  execution list as defined by BaseService
                execution property
            blocks (dict):  dictionary of blocks that looks like this:
                block_name: block instance format
            settings (dict): router settings, these can include
                "clone_signals" and/or any other settings depending on router
                being used
            mgmt_signal_handler (method): method to use to publish
                management signals, receives signal as only parameter
        """
        self.execution = execution
        self.blocks = blocks
        self.settings = settings or {}
        self.mgmt_signal_handler = mgmt_signal_handler
