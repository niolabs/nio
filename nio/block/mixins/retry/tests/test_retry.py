from unittest.mock import MagicMock
from nio.block.base import Block
from nio.testing.block_test_case import NIOBlockTestCase
from nio.block.mixins.retry.retry import Retry
from nio.block.mixins.retry.strategy import BackoffStrategy


class SimpleBackoffStrategy(BackoffStrategy):
    """ A backoff strategy that always retries immediately """

    def should_retry(self):
        return True

class RetryingBlock(Retry, Block):

    def setup_backoff_strategy(self):
        self.use_backoff_strategy(SimpleBackoffStrategy)

class VanillaBlock(Retry, Block):

    def setup_backoff_strategy(self):
        self.use_backoff_strategy(BackoffStrategy, max_retry=1)

class TestRetry(NIOBlockTestCase):

    def test_can_retry(self):
        """Tests that the mixin can retry methods that fail"""
        block = RetryingBlock()
        self.configure_block(block, {})
        # Target func will fail twice, then return a number
        target_func = MagicMock(side_effect=[Exception, Exception, 5])

        # Assert that our function got called 3 times, but that it ultimately
        # returned the correct result
        self.assertEqual(block.execute_with_retry(target_func), 5)
        self.assertEqual(target_func.call_count, 3)

    def test_retry_giveup(self):
        """Tests that an exception is raised if the strategy gives up"""
        SimpleBackoffStrategy.should_retry = MagicMock(
            side_effect=[True, True, False])
        block = RetryingBlock()
        self.configure_block(block, {})
        # Target func will always fail
        target_func = MagicMock(side_effect=Exception)
        # Our backoff strategy will give up on the 3rd try

        # Assert that our function raises its exception and that the mixin
        # still called it 3 times
        with self.assertRaises(Exception):
            block.execute_with_retry(target_func)
        self.assertEqual(target_func.call_count, 3)

    def test_before_retry_called(self):
        """Tests that the block's before_retry funciton is called first"""
        block = RetryingBlock()
        self.configure_block(block, {})
        # Target func will fail twice, then return a number
        target_func = MagicMock(side_effect=[Exception, Exception, 5])
        block.before_retry = MagicMock()

        # Assert that our before retry got called 2 times, one for each retry
        block.execute_with_retry(target_func)
        self.assertEqual(block.before_retry.call_count, 2)

    def test_bad_strategy(self):
        """Test that an exception is raised with a non-BackoffStrategy """
        block = RetryingBlock()
        with self.assertRaises(TypeError):
            block.use_backoff_strategy(Block)
        # An instance of a backoff strategy doesn't count either
        with self.assertRaises(TypeError):
            block.use_backoff_strategy(SimpleBackoffStrategy())

    def test_retry_count(self):
        """Tests that the retry count resets for each execute call"""
        block = VanillaBlock()
        self.configure_block(block, {})
        target_func = MagicMock(side_effect=Exception)
        instances = []
        with self.assertRaises(Exception):
            # each execute_with_retry call should net 2 target_func calls
            block.execute_with_retry(target_func)
        instances.append(block._backoff_strategy)
        self.assertEqual(target_func.call_count, 2)
        with self.assertRaises(Exception):
            block.execute_with_retry(target_func)
        instances.append(block._backoff_strategy)
        self.assertNotEqual(*instances)
        self.assertEqual(target_func.call_count, 4)
