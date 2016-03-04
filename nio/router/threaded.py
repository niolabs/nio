from nio.router.base import BlockRouter
from nio.util.runner import RunnerStatus
from nio.util.threading import spawn


class ThreadedBlockRouter(BlockRouter):

    """A router that delivers signals asynchronously"""

    def deliver_signals(self, block_receiver, signals):
        """ Delivers signals to given block in a new thread """
        spawn(self._safe_process_signals, block_receiver, signals)

    def _safe_process_signals(self, block_receiver, signals):
        try:
            self.notify_signals_to_block(block_receiver, signals)
        except:
            self.status.add(RunnerStatus.error)
            self.logger.exception(
                "{0}.process_signals failed".format(block_receiver.block.name))
