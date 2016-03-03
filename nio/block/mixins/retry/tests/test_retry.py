from unittest.mock import MagicMock
from nio.block.base import Block
from nio.util.support.block_test_case import NIOBlockTestCase
from nio.block.mixins.retry.retry import Retry
from nio.block.mixins.retry.strategy import BackoffStrategy


class SimpleBackoffStrategy(BackoffStrategy):
    """ A backoff strategy that always retries immediately """

    def next_retry(self):
        return True


class RetryingBlock(Retry, Block):

    def configure(self, context):
        super().configure(context)
        self.use_backoff_strategy(SimpleBackoffStrategy)


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
        block = RetryingBlock()
        self.configure_block(block, {})
        # Target func will always fail
        target_func = MagicMock(side_effect=Exception)
        # Our backoff strategy will give up on the 3rd try
        block._backoff_strategy.next_retry = MagicMock(
            side_effect=[True, True, False])

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

    def test_no_strategy(self):
        """Test that a block that doesn't specify a strategy still works.

        We don't expect this to retry at all, but nothing should fail
        """
        class NoStrategy(Retry, Block):
            pass

        block = NoStrategy()
        self.configure_block(block, {})
        # Target func will fail twice, then return a number, not that we ever
        # expect to get there in this test
        target_func = MagicMock(side_effect=[Exception, Exception, 5])

        # Assert that our before retry got called 2 times, one for each retry
        with self.assertRaises(Exception):
            block.execute_with_retry(target_func)
        # We shouldn't have retried at all since we didn't specify a strategy
        self.assertEqual(target_func.call_count, 1)

    def test_bad_strategy(self):
        """Test that an exception is raised with a non-BackoffStrategy """
        block = RetryingBlock()
        with self.assertRaises(TypeError):
            block.use_backoff_strategy(Block)
        # An instance of a backoff strategy doesn't count either
        with self.assertRaises(TypeError):
            block.use_backoff_strategy(SimpleBackoffStrategy())
