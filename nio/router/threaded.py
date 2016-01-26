from nio.router.base import BlockRouter
from nio.common import RunnerStatus
from nio.util.threading import spawn


class ThreadedBaseBlockRouter(BlockRouter):

    """A router that delivers signals asynchronously"""

    def deliver_signals(self, block, signals, input_id):
        """ Delivers signals to given block

        Args:
            block: receiving block
            signals: signals to deliver
            input_id: receiving input

        """
        spawn(self._safe_process_signals, block, signals, input_id)

    def _safe_process_signals(self, block, signals, input_id):
        try:
            block.process_signals(signals, input_id)
        except:
            self.status.add(RunnerStatus.error)
            self._logger.exception(
                "{0}.process_signals failed".format(block.name))
