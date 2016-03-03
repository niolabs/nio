from nio.block.base import Block
from nio.signal.base import Signal
from nio.util.support.block_test_case import NIOBlockTestCase
from time import sleep
from threading import Event
from nio.util.threading import spawn
from nio.block.mixins.retry.retry import Retry


class RetryBlock(Retry, Block):

    def __init__(self, e, num_signals):
        super().__init__()
        self._done_event = e
        self._num_processes_total = num_signals
        self._num_processes_count = 0
        self._retry_count = None

    def process_signals(self, signals):
        """Allow all the signals to be processed before asserting output"""
        output = []
        for signal in signals:
            try:
                output.append(self.execute_with_retry(
                    self._execute,
                    signal=signal))
            except:
                # Execution failed even with retry
                self.logger.exception("Aborting retries")
        self.notify_signals(output)
        self._num_processes_count += 1
        if self._num_processes_count >= self._num_processes_total:
            self._done_event.set()

    def _execute(self, signal):
        sleep(0.1)
        if hasattr(signal, 'error') and signal.error > 0:
            # If it's an 'error' signal riase an exception to retry
            signal.error -= 1
            raise Exception
        return signal

    def before_retry(self, retry_count, **kwargs):
        if self._retry_count:
            self._retry_count += retry_count
        else:
            self._retry_count = retry_count
        return super().before_retry(retry_count, **kwargs)


class TestRetry(NIOBlockTestCase):

    def test_with_no_retry(self):
        """All signals are notified and no retry is ever called"""
        e = Event()
        block = RetryBlock(e, 5)
        self.configure_block(block, {})
        block.start()
        for _ in range(5):
            spawn(block.process_signals, [Signal()])
        e.wait(2)
        block.stop()
        self.assert_num_signals_notified(5)
        # retry_count was never set because we had no failed calls
        self.assertEqual(block._retry_count, None)

    def test_successful_retry(self):
        """All signals are notified and a retry is called for each one"""
        e = Event()
        block = RetryBlock(e, 5)
        self.configure_block(block, {})
        block.start()
        for _ in range(5):
            spawn(block.process_signals, [Signal({'error': 1})])
        e.wait(2)
        block.stop()
        self.assert_num_signals_notified(5)
        # retry_count is 0 because before_retry was called on 0th fail
        self.assertEqual(block._retry_count, 0)

    def test_failed_retry(self):
        """No signals are notified and a retry is called for each one"""
        e = Event()
        block = RetryBlock(e, 5)
        self.configure_block(block, {})
        # Let the block retry up to 100 times
        block.num_retries = 100
        block.start()
        for _ in range(5):
            spawn(block.process_signals, [Signal({'error': 99})])
        e.wait(2)
        block.stop()
        # No signals get notified since we retry forever
        self.assert_num_signals_notified(0)
        # Assert that at least 10 retries (2 for each signal)
        self.assertTrue(block._retry_count >= 10)
