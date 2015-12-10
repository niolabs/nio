from threading import Event
from nio.common.block import MissingBlock
from nio.common.block.base import Block
from nio.common.block.context import BlockContext
from nio.common.block.router.base import BaseBlockRouter, \
    BlockRouterNotStarted, RouterStatus
from nio.common.block.router.threaded import ThreadedBaseBlockRouter
from nio.common.block.controller import BlockController, BlockStatus
from nio.common.block.router.context import RouterContext
from nio.util.support.test_case import NIOTestCase


class SenderBlock(Block):

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__.lower()

    def process_signals(self, signals):
        self.notify_signals(signals)


class ReceiverBlock(Block):

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__.lower()
        self.signal_cache = None

    def process_signals(self, signals):
        self.signal_cache = signals

    def reset_signals(self):
        self.signal_cache = None


class FaultyReceiverBlock(Block):

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__.lower()
        self.signal_cache = None

    def process_signals(self, signals):
        raise RuntimeError("Faulty Receiver Block")

    def reset_signals(self):
        self.signal_cache = None


class TestBlockExecution(object):

    def __init__(self, name, receivers):
        self.name = name
        self.receivers = receivers


class TestThreadedBlockRouter(ThreadedBaseBlockRouter):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._process_event = Event()

    def safe_process_signals(self, block, signals, input_id):
        super().safe_process_signals(block, signals, input_id)
        self._process_event.set()


class TestBlockRouter(NIOTestCase):

    def test_default_router(self):
        """
        Checking that the default router
        delivers signals as intended
        """

        block_router = BaseBlockRouter()
        context = BlockContext(block_router, dict(), dict(), None)

        # create blocks
        sender_block = BlockController(SenderBlock)
        sender_block.configure(context)
        receiver_block = BlockController(ReceiverBlock)
        receiver_block.configure(context)

        # create context initialization data
        blocks = dict(receiverblock=receiver_block,
                      senderblock=sender_block)
        execution = [TestBlockExecution(name="senderblock",
                                        receivers=["receiverblock"])]

        router_context = RouterContext(execution, blocks)

        block_router.configure(router_context)
        block_router.start()

        signals = [1, 2, 3, 4]

        # make sure nothing has been delivered
        self.assertIsNone(receiver_block._block.signal_cache)

        sender_block.process_signals(signals)

        # make sure signals made it
        self.assertIsNotNone(receiver_block._block.signal_cache)
        self.assertEqual(receiver_block._block.signal_cache, signals)

        block_router.stop()

    def test_threaded_router(self):
        """
        Checking that the threaded version of the router
        delivers signals as intended
        """

        block_router = TestThreadedBlockRouter()
        context = BlockContext(block_router, dict(), dict(), None)

        # create blocks
        sender_block = BlockController(SenderBlock)
        sender_block.configure(context)
        receiver_block = BlockController(ReceiverBlock)
        receiver_block.configure(context)

        # create context initialization data
        blocks = dict(receiverblock=receiver_block,
                      senderblock=sender_block)
        execution = [TestBlockExecution(name="senderblock",
                                        receivers=["receiverblock"])]

        router_context = RouterContext(execution, blocks)

        block_router.configure(router_context)
        block_router.start()

        signals = [1, 2, 3, 4]

        # make sure nothing has been delivered
        self.assertIsNone(receiver_block._block.signal_cache)

        sender_block.process_signals(signals)

        # Wait for the thread to report that signals have been processed
        self.assertTrue(block_router._process_event.wait(1))

        # make sure signals made it
        self.assertIsNotNone(receiver_block._block.signal_cache)
        self.assertEqual(receiver_block._block.signal_cache, signals)

        block_router.stop()

    def test_exception_handled(self):
        block_router = TestThreadedBlockRouter()
        context = BlockContext(block_router, dict(), dict(), None)

        sender_block = BlockController(SenderBlock)
        sender_block.configure(context)
        receiver_block = BlockController(FaultyReceiverBlock)
        receiver_block.configure(context)

        # create context initialization data
        blocks = dict(receiverblock=receiver_block,
                      senderblock=sender_block)
        execution = [TestBlockExecution(name="senderblock",
                                        receivers=["receiverblock"])]

        router_context = RouterContext(execution, blocks)

        block_router.configure(router_context)
        block_router.start()

        signals = [1, 2, 3, 4]

        # make sure nothing has been delivered
        self.assertIsNone(receiver_block._block.signal_cache)

        sender_block.process_signals(signals)

        # Wait for the thread to report that signals have been processed
        self.assertTrue(block_router._process_event.wait(1))

        self.assertTrue(block_router.status.is_set(
            RouterStatus.deliver_signal_error))

    def test_not_started_and_stopped_router(self):
        """
        Checking that block router only delivers message to blocks
        when it is started
        """

        block_router = BaseBlockRouter()
        context = BlockContext(block_router, dict(), dict(), None)

        # create blocks
        sender_block = BlockController(SenderBlock)
        sender_block.configure(context)
        receiver_block = BlockController(ReceiverBlock)
        receiver_block.configure(context)

        # create context initialization data
        blocks = dict(receiverblock=receiver_block,
                      senderblock=sender_block)
        execution = [TestBlockExecution(name="senderblock",
                                        receivers=["receiverblock"])]

        router_context = RouterContext(execution, blocks)

        block_router.configure(router_context)

        signals = [1, 2, 3, 4]

        self.assertIsNone(receiver_block._block.signal_cache)

        # catch router not started assertion
        with self.assertRaises(BlockRouterNotStarted):
            sender_block.process_signals(signals)

        block_router.start()
        sender_block.process_signals(signals)

        self.assertIsNotNone(receiver_block._block.signal_cache)
        self.assertEqual(receiver_block._block.signal_cache, signals)

        block_router.stop()

        receiver_block._block.reset_signals()

        # Attempt to send signals and verify that none were sent
        sender_block.process_signals(signals)
        self.assertIsNone(receiver_block._block.signal_cache, 0)

    def test_missing_alias(self):
        """
        Checking an exception is raised when an alias is missing
        """

        block_router = BaseBlockRouter()
        # create blocks
        sender_block = SenderBlock()
        # create context initialization data
        blocks = dict(senderblock=sender_block)
        execution = [TestBlockExecution(name="senderblock",
                                        receivers=["receiverblock"])]

        router_context = RouterContext(execution, blocks)

        self.assertRaises(MissingBlock, block_router.configure,
                          router_context)

    def test_error_skip_notify(self):
        """
        Checking that the default router
        delivers signals as intended
        """

        block_router = BaseBlockRouter()
        context = BlockContext(block_router, dict(), dict(), None)

        # create blocks
        sender_block = BlockController(SenderBlock)
        sender_block.configure(context)
        receiver_block = BlockController(ReceiverBlock)
        receiver_block.configure(context)

        # create context initialization data
        blocks = dict(receiverblock=receiver_block,
                      senderblock=sender_block)
        execution = [TestBlockExecution(name="senderblock",
                                        receivers=["receiverblock"])]

        router_context = RouterContext(execution, blocks)

        block_router.configure(router_context)
        block_router.start()

        signals = [1, 2, 3, 4]
        receiver_block.status = BlockStatus.error

        # make sure nothing has been delivered
        self.assertIsNone(receiver_block._block.signal_cache)

        sender_block.process_signals(signals)

        # make sure signals made it
        self.assertIsNone(receiver_block._block.signal_cache)

        block_router.stop()
