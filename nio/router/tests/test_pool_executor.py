from nio import Signal
from nio.block.base import Block
from nio.block.context import BlockContext
from nio.block.terminals import DEFAULT_TERMINAL
from nio.service.base import BlockExecution
from nio.router.context import RouterContext
from nio.testing.test_case import NIOTestCase


class SenderBlock(Block):

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__.lower()

    def process_signals(self, signals, input_id=DEFAULT_TERMINAL):
        self.notify_signals(signals)


class ReceiverBlock(Block):

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__.lower()
        self.signal_cache = None

    def process_signals(self, signals, input_id=DEFAULT_TERMINAL):
        self.signal_cache = signals

    def reset_signals(self):
        self.signal_cache = None


class BlockExecutionTest(BlockExecution):

    def __init__(self, name, receivers):
        self.name = name
        self.receivers = receivers


class TestBlockRouter(NIOTestCase):

    def test_pool_executor(self):
        """
        Checking that the pool executor version of the router
        delivers signals as intended
        """

        from nio.router.thread_pool_executor import ThreadedPoolExecutorRouter

        block_router = ThreadedPoolExecutorRouter()
        context = BlockContext(block_router, dict(), dict())

        # create blocks
        sender_block = SenderBlock()
        sender_block.configure(context)
        receiver_block = ReceiverBlock()
        receiver_block.configure(context)

        # create context initialization data
        blocks = dict(receiverblock=receiver_block,
                      senderblock=sender_block)
        execution = [BlockExecutionTest(name="senderblock",
                                        receivers=["receiverblock"])]

        router_context = RouterContext(execution, blocks, {"max_workers": 3})

        block_router.do_configure(router_context)
        block_router.do_start()

        signals = [Signal({"1": 1}),
                   Signal({"2": 2}),
                   Signal({"3": 3}),
                   Signal({"4": 4})]

        # make sure nothing has been delivered
        self.assertIsNone(receiver_block.signal_cache)

        sender_block.process_signals(signals)

        # make sure signals made it
        self.assertIsNotNone(receiver_block.signal_cache)
        self.assertEqual(receiver_block.signal_cache, signals)

        block_router.do_stop()
