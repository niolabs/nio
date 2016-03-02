from unittest.mock import patch
from nio import Block
from nio.block.mixins.retry.retry import Retry
from nio.block.mixins.retry.strategies.linear import LinearBackoff
from nio.util.support.test_case import NIOTestCaseNoModules


class LinearBackoffBlock(Retry, Block):
    """ An example of a block that uses a Linear Backoff strategy """

    def __init__(self, max_retries=-1, multiplier=1):
        super().__init__()
        self._max_retries = max_retries
        self._multiplier = multiplier

    def configure(self, context):
        self.use_backoff_strategy(
            LinearBackoff, max_retries=self._max_retries,
            multiplier=self._multiplier)


class TestLinearBackoff(NIOTestCaseNoModules):

    def assert_next_retry_sleeps_for(self, block, num_seconds):
        """Make sure that given a failure the block will sleep for some time"""
        with patch('nio.block.mixins.retry.strategies.linear.sleep') as sleep:
            block._backoff_strategy.request_failed(Exception())
            block._backoff_strategy.next_retry()
            sleep.assert_called_once_with(num_seconds)

    def test_default(self):
        """Test the default behavior of the linear backoff"""
        block = LinearBackoffBlock()
        block.configure(None)
        # First failure should sleep for 1 second
        self.assert_next_retry_sleeps_for(block, 1)
        # Second failure should sleep for 2 seconds
        self.assert_next_retry_sleeps_for(block, 2)
        # Third failure should sleep for 3 seconds
        self.assert_next_retry_sleeps_for(block, 3)
        # Success should reset, so next failure will be 1 second
        block._backoff_strategy.request_succeeded()
        self.assert_next_retry_sleeps_for(block, 1)

    def test_multiplier(self):
        """Test that we can multiply the number of seconds to sleep"""
        block = LinearBackoffBlock(multiplier=3.14)
        block.configure(None)
        # Execute 3 retries and make sure we multiply each time
        self.assert_next_retry_sleeps_for(block, 3.14)
        self.assert_next_retry_sleeps_for(block, 6.28)
        self.assert_next_retry_sleeps_for(block, 9.42)

    def test_max_retries(self):
        """Test that we can cap the number of retries"""
        block = LinearBackoffBlock(max_retries=2)
        block.configure(None)
        # Execute 3 retries, but make sure only the first two actually sleep
        self.assert_next_retry_sleeps_for(block, 1)
        self.assert_next_retry_sleeps_for(block, 2)
        # Last retry should return false and not sleep
        with patch('nio.block.mixins.retry.strategies.linear.sleep') as sleep:
            block._backoff_strategy.request_failed(Exception())
            self.assertFalse(block._backoff_strategy.next_retry())
            sleep.assert_not_called()
