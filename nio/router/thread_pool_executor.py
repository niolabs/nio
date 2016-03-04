from nio.router.base import BlockRouter
from concurrent.futures.thread import ThreadPoolExecutor


class ThreadedPoolExecutorRouter(BlockRouter):
    """ A router that delivers signals asynchronously in a thread pool

    This router caps the number of threads used for block's signal receiving.
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

    def deliver_signals(self, block_receiver, signals):
        """ Deliver the signals inside of the thread executor """
        self._executor.submit(
            self.notify_signals_to_block, block_receiver, signals)
