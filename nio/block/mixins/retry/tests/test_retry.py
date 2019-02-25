from threading import Event
from unittest.mock import MagicMock, patch
from nio.block.base import Block
from nio.util.threading import spawn
from nio.testing.block_test_case import NIOBlockTestCase
from nio.block.mixins.retry.retry import Retry
from nio.block.mixins.retry.strategy import BackoffStrategy


class SimpleBackoffStrategy(BackoffStrategy):
    """ A backoff strategy that always retries immediately """

    def should_retry(self):
        return True

    def wait_for_retry(self):
        pass


class EventDrivenBackoffStrategy(BackoffStrategy):

    def __init__(self, retry_event, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._retry_event = retry_event

    def wait_for_retry(self):
        result = self._retry_event.wait(2)
        if not result:
            raise AssertionError('retry event not set')


class NoRetryBlock(Retry, Block):

    def setup_backoff_strategy(self):
        self.use_backoff_strategy(SimpleBackoffStrategy)

    def should_retry(self):
        return False


class RetryingBlock(Retry, Block):

    def setup_backoff_strategy(self):
        self.use_backoff_strategy(SimpleBackoffStrategy)


class VanillaBlock(Retry, Block):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._retry_event = Event()

    def setup_backoff_strategy(self):
        self.use_backoff_strategy(
            EventDrivenBackoffStrategy,
            retry_event=self._retry_event,
            max_retry=2)


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
        """Tests that the exception is raised if the strategy gives up"""
        block = RetryingBlock()
        self.configure_block(block, {})

        class CustomException(Exception):
            pass

        # Target func will always fail
        target_func = MagicMock(side_effect=CustomException)
        # Our backoff strategy will give up on the 3rd try

        with patch.object(SimpleBackoffStrategy, 'should_retry',
                          side_effect=[True, True, False]):
            # Assert that our function raises its exception and that the mixin
            # still called it 3 times
            with self.assertRaises(CustomException):
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

    def test_max_retry_exhausted_called(self):
        """Tests that the block's max_retry_exhausted function is called"""
        block = VanillaBlock()
        self.configure_block(block, {})
        
        class CustomException(Exception):
            pass

        this_exception = CustomException()
        # target_func fails forever
        target_func = MagicMock(side_effect=this_exception)
        # max_retry_exhausted needs to be mocked for assertions while also
        # raising the original exception
        block.max_retry_exhausted = MagicMock(side_effect=this_exception)

        target_func_call = spawn(block.execute_with_retry, target_func)
        block._retry_event.set()  # don't wait for EventDrivenBackoffStrategy
        with self.assertRaises(CustomException):
            target_func_call.join()
        # max_retry_exhausted was called with the original exception
        self.assertEqual(block.max_retry_exhausted.call_count, 1)
        block.max_retry_exhausted.assert_called_once_with(this_exception)

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

        class CustomException(Exception):
            pass

        target_func_1 = MagicMock(side_effect=CustomException)
        target_func_2 = MagicMock(side_effect=CustomException)
        call_1 = spawn(block.execute_with_retry, target_func_1)
        call_2 = spawn(block.execute_with_retry, target_func_2)
        block._retry_event.set()
        with self.assertRaises(CustomException):
            call_1.join()
        with self.assertRaises(CustomException):
            call_2.join()
        # each execute_with_retry call should net 3 target_func calls
        self.assertEqual(target_func_1.call_count, 3)
        self.assertEqual(target_func_2.call_count, 3)

    def test_should_retry_method(self):
        """Block implements a `should_retry` method which takes precedence
        over the backoff strategy's method by the same name."""
        block = NoRetryBlock()
        self.configure_block(block, {})

        class CustomException(Exception):
            pass

        # target_func fails forever
        target_func = MagicMock(side_effect=CustomException)

        # SimpleBackoffStrategy was ignored and no retries were executed
        with self.assertRaises(CustomException):
            block.execute_with_retry(target_func)
        # self.assertEqual(target_func.call_count, 1)
