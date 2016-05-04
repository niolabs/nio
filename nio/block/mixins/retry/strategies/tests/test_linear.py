from unittest.mock import patch
from nio import Block
from nio.block.mixins.retry.retry import Retry
from nio.testing.block_test_case import NIOBlockTestCase


class LinearBackoffBlock(Retry, Block):
    """ An example of a block that uses a Linear Backoff strategy """
    pass


class TestLinearBackoff(NIOBlockTestCase):

    def assert_next_retry_sleeps_for(self, block, num_seconds):
        """Make sure that given a failure the block will sleep for some time"""
        with patch('nio.block.mixins.retry.strategies.linear.sleep') as sleep:
            block._backoff_strategy.request_failed(Exception())
            if block._backoff_strategy.should_retry():
                block._backoff_strategy.wait_for_retry()
            sleep.assert_called_once_with(num_seconds)

    def test_default(self):
        """Test the default behavior of the linear backoff"""
        block = LinearBackoffBlock()
        self.configure_block(block, {
            "retry_options": {
                "strategy": "linear"
            }
        })
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
        block = LinearBackoffBlock()
        self.configure_block(block, {
            "retry_options": {
                "strategy": "linear",
                "multiplier": 3.14
            }
        })
        # Execute 3 retries and make sure we multiply each time
        self.assert_next_retry_sleeps_for(block, 3.14)
        self.assert_next_retry_sleeps_for(block, 6.28)
        self.assert_next_retry_sleeps_for(block, 9.42)

    def test_indefinite(self):
        """Test that retries can happen indefinitely """
        block = LinearBackoffBlock()
        self.configure_block(block, {
            "retry_options": {
                "strategy": "linear",
                "max_retry": 3,
                "indefinite": True
            }
        })
        # Should count to three retries then keep trying, every 3 seconds
        self.assert_next_retry_sleeps_for(block, 1)
        self.assert_next_retry_sleeps_for(block, 2)
        self.assert_next_retry_sleeps_for(block, 3)
        self.assert_next_retry_sleeps_for(block, 3)
        self.assert_next_retry_sleeps_for(block, 3)

    def test_multiplied_indefinite(self):
        """Test that retries can happen indefinitely """
        block = LinearBackoffBlock()
        self.configure_block(block, {
            "retry_options": {
                "strategy": "linear",
                "max_retry": 3,
                "multiplier": 2,
                "indefinite": True
            }
        })
        # Should count to three retries then keep trying, every 3*2 seconds
        self.assert_next_retry_sleeps_for(block, 2)
        self.assert_next_retry_sleeps_for(block, 4)
        self.assert_next_retry_sleeps_for(block, 6)
        self.assert_next_retry_sleeps_for(block, 6)
        self.assert_next_retry_sleeps_for(block, 6)

    def test_max_retries(self):
        """Test that we can cap the number of retries"""
        block = LinearBackoffBlock()
        self.configure_block(block, {
            "retry_options": {
                "strategy": "linear",
                "max_retry": 2
            }
        })
        # Execute 3 retries, but make sure only the first two actually sleep
        self.assert_next_retry_sleeps_for(block, 1)
        self.assert_next_retry_sleeps_for(block, 2)
        # Last retry should return false and not sleep
        with patch('nio.block.mixins.retry.strategies.linear.sleep') as sleep:
            block._backoff_strategy.request_failed(Exception())
            self.assertFalse(block._backoff_strategy.should_retry())
            sleep.assert_not_called()
