from unittest.mock import patch, MagicMock
from nio import Block
from nio.block.mixins.retry.retry import Retry
from nio.testing.block_test_case import NIOBlockTestCase


class ExponentialBackoffBlock(Retry, Block):
    """ An example of a block that uses a Exponential Backoff strategy """
    pass


class TestExponentialBackoff(NIOBlockTestCase):

    def assert_next_retry_sleeps_for(self, block, num_seconds):
        """Make sure that given a failure the block will sleep for some time"""
        sleep_path = 'nio.block.mixins.retry.strategies.exponential.sleep'
        with patch(sleep_path) as sleep:
            block._backoff_strategy.request_failed(Exception())
            if block._backoff_strategy.should_retry():
                block._backoff_strategy.wait_for_retry()
            sleep.assert_called_once_with(num_seconds)

    def test_default(self):
        """Test the default behavior of the exponential backoff"""
        block = ExponentialBackoffBlock()
        self.configure_block(block, {
            "retry_options": {
                "strategy": "exponential"
            }
        })
        target_func = MagicMock()
        block.execute_with_retry(target_func)
        # First failure should sleep for 1 second
        self.assert_next_retry_sleeps_for(block, 1)
        # Second failure should sleep for 2 seconds
        self.assert_next_retry_sleeps_for(block, 2)
        # Third failure should sleep for 3 seconds
        self.assert_next_retry_sleeps_for(block, 4)
        # Success should reset, so next failure will be 1 second
        block._backoff_strategy.request_succeeded()
        self.assert_next_retry_sleeps_for(block, 1)

    def test_multiplier(self):
        """Test that we can multiply the number of seconds to sleep"""
        block = ExponentialBackoffBlock()
        self.configure_block(block, {
            "retry_options": {
                "strategy": "exponential",
                "multiplier": 3.14
            }
        })
        target_func = MagicMock()
        block.execute_with_retry(target_func)
        # Execute 3 retries and make sure we multiply each time
        self.assert_next_retry_sleeps_for(block, 3.14)
        self.assert_next_retry_sleeps_for(block, 6.28)
        self.assert_next_retry_sleeps_for(block, 12.56)
        self.assert_next_retry_sleeps_for(block, 25.12)

    def test_indefinite(self):
        """Test that retries can happen indefinitely """
        block = ExponentialBackoffBlock()
        self.configure_block(block, {
            "retry_options": {
                "strategy": "exponential",
                "max_retry": 4,
                "indefinite": True
            }
        })
        target_func = MagicMock()
        block.execute_with_retry(target_func)
        # Should count to three retries then keep trying, every 2**3 seconds
        self.assert_next_retry_sleeps_for(block, 1)
        self.assert_next_retry_sleeps_for(block, 2)
        self.assert_next_retry_sleeps_for(block, 4)
        self.assert_next_retry_sleeps_for(block, 8)
        self.assert_next_retry_sleeps_for(block, 8)
        self.assert_next_retry_sleeps_for(block, 8)

    def test_multiplied_indefinite(self):
        """Test that retries can happen indefinitely """
        block = ExponentialBackoffBlock()
        self.configure_block(block, {
            "retry_options": {
                "strategy": "exponential",
                "max_retry": 3,
                "multiplier": 3,
                "indefinite": True
            }
        })
        target_func = MagicMock()
        block.execute_with_retry(target_func)
        # Should count to three retries then keep trying, every 3*2**2 seconds
        self.assert_next_retry_sleeps_for(block, 3)
        self.assert_next_retry_sleeps_for(block, 6)
        self.assert_next_retry_sleeps_for(block, 12)
        self.assert_next_retry_sleeps_for(block, 12)
        self.assert_next_retry_sleeps_for(block, 12)

    def test_max_retries(self):
        """Test that we can cap the number of retries"""
        block = ExponentialBackoffBlock()
        self.configure_block(block, {
            "retry_options": {
                "strategy": "exponential",
                "max_retry": 2
            }
        })
        target_func = MagicMock()
        block.execute_with_retry(target_func)
        # Execute 3 retries, but make sure only the first two actually sleep
        self.assert_next_retry_sleeps_for(block, 1)
        self.assert_next_retry_sleeps_for(block, 2)
        # Last retry should return false and not sleep
        sleep_path = 'nio.block.mixins.retry.strategies.exponential.sleep'
        with patch(sleep_path) as sleep:
            block._backoff_strategy.request_failed(Exception())
            self.assertFalse(block._backoff_strategy.should_retry())
            sleep.assert_not_called()
