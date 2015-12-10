from nio.common.block.router.base import BaseBlockRouter, RouterStatus
from nio.util.threading import spawn


class ThreadedBaseBlockRouter(BaseBlockRouter):

    """An object that contains blocks and can handle when blocks notify
    signals.

    """

    def deliver_signals(self, block, signals, input_id):
        spawn(self.safe_process_signals, block, signals, input_id)

    def safe_process_signals(self, block, signals, input_id):
        try:
            block.process_signals(signals, input_id)
        except:
            self.status.add(RouterStatus.deliver_signal_error)
            self._logger.exception(
                "{0}.process_signals failed".format(block.name))
