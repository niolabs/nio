from unittest.mock import patch, MagicMock
from nio import Block
from nio.block.mixins.retry.retry import Retry
from nio.testing.block_test_case import NIOBlockTestCase


class ExponentialBackoffBlock(Retry, Block):
    """ An example of a block that uses a Exponential Backoff strategy """
    pass


class TestExponentialBackoff(NIOBlockTestCase):

    def assert_next_retry_sleeps_for(self, block, retry_num, num_seconds):
        """Make sure that given a failure the block will sleep for some time"""
        sleep_path = 'nio.block.mixins.retry.strategies.exponential.sleep'
        with patch(sleep_path) as sleep:
            # block._backoff_strategy.request_failed(Exception())
            if block._backoff_strategy.should_retry(retry_num):
                block._backoff_strategy.wait_for_retry(retry_num)
            sleep.assert_called_once_with(num_seconds)

    def test_default(self):
        """Test the default behavior of the exponential backoff"""
        retry_num = 0
        block = ExponentialBackoffBlock()
        self.configure_block(block, {
            "retry_options": {
                "strategy": "exponential"
            }
        })
        target_func = MagicMock()
        block.execute_with_retry(target_func)
        retry_num += 1
        # First failure should sleep for 1 second
        self.assert_next_retry_sleeps_for(block, retry_num, 1)
        retry_num += 1
        # Second failure should sleep for 2 seconds
        self.assert_next_retry_sleeps_for(block, retry_num, 2)
        retry_num += 1
        # Third failure should sleep for 3 seconds
        self.assert_next_retry_sleeps_for(block, retry_num, 4)
        retry_num += 1
        # Success should reset, so next failure will be 1 second
        retry_num = 1
        self.assert_next_retry_sleeps_for(block, retry_num, 1)

    def test_multiplier(self):
        """Test that we can multiply the number of seconds to sleep"""
        retry_num = 0
        block = ExponentialBackoffBlock()
        self.configure_block(block, {
            "retry_options": {
                "strategy": "exponential",
                "multiplier": 3.14
            }
        })
        target_func = MagicMock()
        block.execute_with_retry(target_func)
        retry_num += 1
        # Execute 3 retries and make sure we multiply each time
        self.assert_next_retry_sleeps_for(block, retry_num, 3.14)
        retry_num += 1
        self.assert_next_retry_sleeps_for(block, retry_num, 6.28)
        retry_num += 1
        self.assert_next_retry_sleeps_for(block, retry_num, 12.56)
        retry_num += 1
        self.assert_next_retry_sleeps_for(block, retry_num, 25.12)

    def test_indefinite(self):
        """Test that retries can happen indefinitely """
        retry_num = 0
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
        retry_num += 1
        # Should count to three retries then keep trying, every 2**3 seconds
        self.assert_next_retry_sleeps_for(block, retry_num, 1)
        retry_num += 1
        self.assert_next_retry_sleeps_for(block, retry_num, 2)
        retry_num += 1
        self.assert_next_retry_sleeps_for(block, retry_num, 4)
        retry_num += 1
        self.assert_next_retry_sleeps_for(block, retry_num, 8)
        retry_num += 1
        self.assert_next_retry_sleeps_for(block, retry_num, 8)
        retry_num += 1
        self.assert_next_retry_sleeps_for(block, retry_num, 8)

    def test_multiplied_indefinite(self):
        """Test that retries can happen indefinitely """
        retry_num = 0
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
        retry_num += 1
        # Should count to three retries then keep trying, every 3*2**2 seconds
        self.assert_next_retry_sleeps_for(block, retry_num, 3)
        retry_num += 1
        self.assert_next_retry_sleeps_for(block, retry_num, 6)
        retry_num += 1
        self.assert_next_retry_sleeps_for(block, retry_num, 12)
        retry_num += 1
        self.assert_next_retry_sleeps_for(block, retry_num, 12)
        retry_num += 1
        self.assert_next_retry_sleeps_for(block, retry_num, 12)

    def test_max_retries(self):
        """Test that we can cap the number of retries"""
        retry_num = 0
        block = ExponentialBackoffBlock()
        self.configure_block(block, {
            "retry_options": {
                "strategy": "exponential",
                "max_retry": 2
            }
        })
        target_func = MagicMock()
        block.execute_with_retry(target_func)
        retry_num += 1
        # Execute 3 retries, but make sure only the first two actually sleep
        self.assert_next_retry_sleeps_for(block, retry_num, 1)
        retry_num += 1
        self.assert_next_retry_sleeps_for(block, retry_num, 2)
        retry_num += 1
        # Last retry should return false and not sleep
        sleep_path = 'nio.block.mixins.retry.strategies.exponential.sleep'
        with patch(sleep_path) as sleep:
            # block._backoff_strategy.request_failed(Exception())
            self.assertFalse(block._backoff_strategy.should_retry(retry_num))
            sleep.assert_not_called()
