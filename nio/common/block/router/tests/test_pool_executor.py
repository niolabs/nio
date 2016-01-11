from nio.block.base import Block
from nio.block.context import BlockContext
from nio.common.block.controller import BlockController
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


class TestBlockExecution(object):

    def __init__(self, name, receivers):
        self.name = name
        self.receivers = receivers


class TestBlockRouter(NIOTestCase):

    def get_provider_settings(self):
        """ Override this method for specifying settings
        for the config provider
        """
        return {"block_router.cfg": {"max_workers": 3}}

    def test_pool_executor(self):
        """
        Checking that the pool executor version of the router
        delivers signals as intended
        """

        from nio.common.block.router.thread_pool_executor \
            import ThreadedPoolExecutorRouter

        block_router = ThreadedPoolExecutorRouter()
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
