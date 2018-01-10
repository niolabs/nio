from time import sleep
from threading import Event
from unittest.mock import MagicMock
from nio.block.base import Block
from nio.testing.block_test_case import NIOBlockTestCase
from nio.block.mixins.retry.retry import Retry
from nio.block.mixins.retry.strategy import BackoffStrategy
from nio.util.threading import spawn


class SleepBackoffStrategy(BackoffStrategy):
    """ A backoff strategy that sleeps """

    def __init__(self, sleep_time):
        super().__init__()
        self._sleep_time = sleep_time

    def should_retry(self, retry_num):
        return True

    def wait_for_retry(self):
        sleep(self._sleep_time)


class RetryingBlock(Retry, Block):

    def __init__(self, sleep_retry_time):
        super().__init__()
        self._sleep_time = sleep_retry_time

    def setup_backoff_strategy(self):
        self.use_backoff_strategy(SleepBackoffStrategy, self._sleep_time)


class TestCancelRetry(NIOBlockTestCase):

    def test_stop_loop(self):
        """Tests that the retry mixin loop can be stopped/cancelled"""
        sleep_retry_time = 0.01
        block = RetryingBlock(sleep_retry_time)
        self.configure_block(block, {})
        # Target func will fail
        target_func = MagicMock(side_effect=[Exception, Exception, Exception])

        stop_retry_event = Event()
        execute_thread = spawn(block.execute_with_retry, target_func,
                               stop_retry_event=stop_retry_event)
        sleep(sleep_retry_time)
        # set event that will stop retrying mechanism
        stop_retry_event.set()
        # allow double sleep retry time when joining
        execute_thread.join(2*sleep_retry_time)

        # assert that thread terminated
        self.assertFalse(execute_thread.is_alive())

        # assert target was called
        target_func.assert_any_call()

    def test_event_argument(self):
        """ Asserts that 'stop_retry_event' argument type is checked against
        """
        block = RetryingBlock(0)
        self.configure_block(block, {})
        target_func = MagicMock(side_effect=[Exception])

        stop_retry_event = "not an event instance"
        # assert that argument type is checked against
        with self.assertRaises(TypeError):
            block.execute_with_retry(target_func,
                                     stop_retry_event=stop_retry_event)

        # assert that target_func was not called since type checking failed
        self.assertEqual(target_func.call_count, 0)
