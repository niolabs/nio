from nio.common.block.router.base import BaseBlockRouter
from concurrent.futures.thread import ThreadPoolExecutor


class ThreadedPoolExecutorRouter(BaseBlockRouter):
    """ A router that caps the number of threads used for block's
    signal receiving.

    """

    def __init__(self):
        super().__init__()
        self._executor = None

    def configure(self, context):
        super().configure(context)

        max_workers = context.settings.get("max_workers", 50)
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def deliver_signals(self, block, signals, input_id):
        self._executor.submit(block.process_signals, signals, input_id)
