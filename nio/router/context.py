class RouterContext(object):

    """ Maintains information needed to configure a block router """

    def __init__(self, execution, blocks, settings=None):
        """Initializes a router context.

        Args:
            execution (list):  execution list as defined by BaseService
                execution property
            blocks (dict):  dictionary of blocks that looks like this:
                block_name: block instance format
            settings (dict): router settings, these can include
                "clone_signals" and/or any other settings depending on router
                being used
        """
        self.execution = execution
        self.blocks = blocks
        self.settings = settings or {}
