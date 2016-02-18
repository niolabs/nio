from time import sleep
from threading import Event
from nio.block.base import Block
from nio.block.context import BlockContext
from nio.service.base import BlockExecution
from nio.router.context import RouterContext
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
        self.signal_received = Event()

    def process_signals(self, signals, input_id='default'):
        # Wait half a second before setting the event
        # The calling thread should continue executing while this one is
        # sleeping
        sleep(0.5)
        self.signal_received.set()


class BlockExecutionTest(BlockExecution):

    def __init__(self, name, receivers):
        self.name = name
        self.receivers = receivers


class TestThreadedRouter(NIOTestCase):

    def test_threaded(self):
        """Checking that the threaded version of the router delivers signals"""

        from nio.router.threaded import ThreadedBlockRouter

        block_router = ThreadedBlockRouter()
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

        router_context = RouterContext(execution, blocks, {})

        block_router.do_configure(router_context)
        block_router.do_start()

        signals = [1, 2, 3, 4]

        # make sure nothing has been delivered
        self.assertFalse(receiver_block.signal_received.is_set())

        sender_block.process_signals(signals)
        # We should still have nothing, it will take half a second for the
        # event to be set. But our thread will continue execution
        self.assertFalse(receiver_block.signal_received.is_set())

        # Wait up to one second, but we don't expect the timeout to occur
        self.assertTrue(receiver_block.signal_received.wait(1))
        self.assertTrue(receiver_block.signal_received.is_set())

        block_router.do_stop()
