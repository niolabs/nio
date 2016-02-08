from nio.router.base import BlockRouter
from concurrent.futures.thread import ThreadPoolExecutor


class ThreadedPoolExecutorRouter(BlockRouter):
    """ A router that delivers signals asynchronously and caps the number of
    threads used for block's signal receiving.
    """

    def __init__(self):
        """ Create a new threaded pool executor router """
        super().__init__()
        self._executor = None

    def configure(self, context):
        """ Configures router

        Instantiates actual pool executor
        """
        super().configure(context)

        max_workers = context.settings.get("max_workers", 50)
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def deliver_signals(self, block, signals, input_id):
        """ Delivers signals to given block

        Args:
            block: receiving block
            signals: signals to deliver
            input_id: receiving input

        """
        self._executor.submit(block.process_signals, signals, input_id)
