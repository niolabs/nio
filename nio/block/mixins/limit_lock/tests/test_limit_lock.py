from unittest.mock import MagicMock
from nio.block.base import Block
from nio.signal.base import Signal
from nio.util.support.block_test_case import NIOBlockTestCase
from time import sleep
from threading import Event
from nio.util.threading import spawn
from nio.block.mixins.limit_lock.limit_lock import LimitLock, LockQueueFull


class LockBlock(LimitLock, Block):

    def __init__(self, e, num_signals, num_locks):
        super().__init__()
        self._done_event = e
        self._num_processes_total = num_signals
        self._num_locks = num_locks
        self._num_processes_count = 0
        self._retry_count = None
        self._number_of_lock_queue_full_errors = 0

    def process_signals(self, signals):
        """Allow all the signals to be processed before asserting output"""
        output = []
        for signal in signals:
            try:
                output_signal = self.execute_with_lock(
                    self._execute, self._num_locks, signal=signal)
                if output_signal:
                    output.append(output_signal)
            except LockQueueFull:
                # Keep track of the number of signals that are blocked
                self._number_of_lock_queue_full_errors += 1
            except:
                pass
        self.notify_signals(output)
        # Keep track of the number of signals that complese processing
        self._num_processes_count += 1
        if self._num_processes_count >= self._num_processes_total:
            self._done_event.set()

    def _execute(self, signal):
        sleep(0.1)
        return signal


class TestLock(NIOBlockTestCase):

    def test_with_one_lock(self):
        """Only the first signal is notified and the others are dropped"""
        e = Event()
        block = LockBlock(e, 5, 1)
        self.configure_block(block, {"name": "LockBlock"})
        block.start()
        for _ in range(5):
            spawn(block.process_signals, [Signal()])
        e.wait(2)
        block.stop()
        self.assert_num_signals_notified(1)
        self.assertEqual(block._number_of_locks, 0)
        # One signal is notifed and 4 are blocked
        self.assertEqual(block._number_of_lock_queue_full_errors, 4)
        # Confirm that all signals were processed
        self.assertEqual(block._num_processes_count, 5)

    def test_with_no_locks(self):
        """No signals get through"""
        e = Event()
        block = LockBlock(e, 5, 0)
        self.configure_block(block, {})
        block.start()
        for _ in range(5):
            spawn(block.process_signals, [Signal()])
        e.wait(2)
        block.stop()
        self.assert_num_signals_notified(0)
        self.assertEqual(block._number_of_locks, 0)
        # All 5 signals are blocked
        self.assertEqual(block._number_of_lock_queue_full_errors, 5)
        # Confirm that all signals were processed
        self.assertEqual(block._num_processes_count, 5)

    def test_with_enough_locks(self):
        """All the signals get through since we have enought locks"""
        e = Event()
        block = LockBlock(e, 5, 5)
        self.configure_block(block, {})
        block.start()
        for _ in range(5):
            spawn(block.process_signals, [Signal()])
        e.wait(2)
        block.stop()
        self.assert_num_signals_notified(5)
        self.assertEqual(block._number_of_locks, 0)
        # All 5 signals are notified and none get blocked
        self.assertEqual(block._number_of_lock_queue_full_errors, 0)
        # Confirm that all signals were processed
        self.assertEqual(block._num_processes_count, 5)

    def test_exception_in_execute_method(self):
        """Handle exceptions in execute method"""
        def execute_method():
            raise Exception
        block = LimitLock()
        block._logger = MagicMock()
        self.assertRaises(Exception,
                          block.execute_with_lock, execute_method, 1)
        # The lock needs to be released after the exception
        self.assertEqual(block._number_of_locks, 0)

    def test_max_locks(self):
        """Handle exception when max locks is reached"""
        def execute_method():
            pass
        block = LimitLock()
        block._logger = MagicMock()
        # max locks is 0 so it will always be full
        self.assertRaises(LockQueueFull,
                          block.execute_with_lock, execute_method, 0)
        self.assertEqual(block._number_of_locks, 0)

    def test_execute_method_args(self):
        """Check that args work in execute method"""
        def execute_method(arg1, arg2):
            self.assertEqual(arg1, 1)
            self.assertEqual(arg2, 2)
        block = LimitLock()
        block._logger = MagicMock()
        block.execute_with_lock(execute_method, 1, 1, 2)
        self.assertEqual(block._number_of_locks, 0)

    def test_execute_method_kwargs(self):
        """Check that kwargs work in execute method"""
        def execute_method(arg1, arg2):
            self.assertEqual(arg1, 1)
            self.assertEqual(arg2, 2)
        block = LimitLock()
        block._logger = MagicMock()
        block.execute_with_lock(execute_method, 1, arg1=1, arg2=2)
        self.assertEqual(block._number_of_locks, 0)

    def test_execute_method_args_and_kwargs(self):
        """Check that args and kwargs work together in execute method"""
        def execute_method(arg1, arg2, arg3=-3, arg4=-4):
            self.assertEqual(arg1, 1)
            self.assertEqual(arg2, 2)
            self.assertEqual(arg3, -3)
            self.assertEqual(arg4, 4)
        block = LimitLock()
        block._logger = MagicMock()
        block.execute_with_lock(execute_method, 1, 1, 2, arg4=4)
        self.assertEqual(block._number_of_locks, 0)
