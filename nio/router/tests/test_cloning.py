from unittest.mock import patch

from nio.block.base import Block
from nio.block.context import BlockContext
from nio.block.terminals import DEFAULT_TERMINAL
from nio.router.base import BlockRouter
from nio.router.context import RouterContext
from nio.service.base import BlockExecution
from nio.signal.base import Signal
from nio.util.support.test_case import NIOTestCase


class SenderBlock(Block):

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__.lower()

    def process_signals(self, signals, input_id=DEFAULT_TERMINAL):
        self.notify_signals(signals)


class ReceiverBlock1(Block):

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__.lower()
        self.signal_cache = None

    def process_signals(self, signals, input_id=DEFAULT_TERMINAL):
        # add attribute
        for signal in signals:
            setattr(signal, "receiver", self.__class__.__name__)
        self.signal_cache = signals

    def reset_signals(self):
        self.signal_cache = None


class ReceiverBlock2(Block):

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__.lower()
        self.signal_cache = None

    def process_signals(self, signals, input_id=DEFAULT_TERMINAL):
        for signal in signals:
            setattr(signal, "receiver", self.__class__.__name__)
        self.signal_cache = signals

    def reset_signals(self):
        self.signal_cache = None


class BlockExecutionTest(BlockExecution):

    def __init__(self, name, receivers):
        self.name = name
        self.receivers = receivers


class TestCloningSignals(NIOTestCase):

    def test_cloning(self):
        """
        Checking that the default router
        delivers signals as intended
        """

        block_router = BlockRouter()
        context = BlockContext(block_router, dict())

        # create blocks
        sender_block = SenderBlock()
        sender_block.configure(context)
        receiver_block1 = ReceiverBlock1()
        receiver_block1.configure(context)
        receiver_block2 = ReceiverBlock2()
        receiver_block2.configure(context)

        # create context initialization data
        blocks = dict(receiverblock1=receiver_block1,
                      receiverblock2=receiver_block2,
                      senderblock=sender_block)
        execution = [BlockExecutionTest(name="senderblock",
                                        receivers=["receiverblock1",
                                                   "receiverblock2"])]

        router_context = RouterContext(execution, blocks,
                                       {"clone_signals": True})

        block_router.do_configure(router_context)
        block_router.do_start()

        common_attribute = "common attribute"
        common_value = "common value"
        signals = [Signal({common_attribute: common_value})]

        # make sure nothing has been delivered
        self.assertIsNone(receiver_block1.signal_cache)
        self.assertIsNone(receiver_block2.signal_cache)

        sender_block.process_signals(signals)

        # make sure signals made it
        self.assertIsNotNone(receiver_block1.signal_cache)
        for i in range(len(signals)):
            self.assertEqual(getattr(receiver_block1.signal_cache[i],
                                     common_attribute),
                             getattr(signals[i], common_attribute))

        self.assertIsNotNone(receiver_block2.signal_cache)
        for i in range(len(signals)):
            self.assertEqual(getattr(receiver_block2.signal_cache[i],
                                     common_attribute),
                             getattr(signals[i], common_attribute))

        self.assertNotEqual(receiver_block1.signal_cache,
                            receiver_block2.signal_cache)

        # assert that signals received differ from original signals
        self.assertNotEqual(receiver_block1.signal_cache,
                            signals)
        self.assertNotEqual(receiver_block2.signal_cache,
                            signals)

        block_router.do_stop()

    def test_deepcopy_failure(self):
        """ Asserts that when deepcopy fails, signals are delivered anyways,
        only they are not copied, and instead original signals are delivered
        """

        block_router = BlockRouter()
        context = BlockContext(block_router, dict())

        # create blocks
        sender_block = SenderBlock()
        sender_block.configure(context)
        receiver_block1 = ReceiverBlock1()
        receiver_block1.configure(context)
        receiver_block2 = ReceiverBlock2()
        receiver_block2.configure(context)

        # create context initialization data
        blocks = dict(receiverblock1=receiver_block1,
                      receiverblock2=receiver_block2,
                      senderblock=sender_block)
        execution = [BlockExecutionTest(name="senderblock",
                                        receivers=["receiverblock1",
                                                   "receiverblock2"])]

        router_context = RouterContext(execution, blocks)

        block_router.do_configure(router_context)
        block_router.do_start()

        common_attribute = "common attribute"
        common_value = "common value"
        signals = [Signal({common_attribute: common_value})]

        # make sure nothing has been delivered
        self.assertIsNone(receiver_block1.signal_cache)
        self.assertIsNone(receiver_block2.signal_cache)

        # patching deepcopy, making it fail
        with patch('nio.router.base.deepcopy',
                   side_effect=Exception("causing deepcopy failure")):
            sender_block.process_signals(signals)

        # make sure signals made it
        self.assertIsNotNone(receiver_block1.signal_cache)
        for i in range(len(signals)):
            self.assertEqual(getattr(receiver_block1.signal_cache[i],
                                     common_attribute),
                             getattr(signals[i], common_attribute))

        self.assertIsNotNone(receiver_block2.signal_cache)
        for i in range(len(signals)):
            self.assertEqual(getattr(receiver_block2.signal_cache[i],
                                     common_attribute),
                             getattr(signals[i], common_attribute))

        # asserting that both receiver blocks received the same signal
        # even though a deepcopy was intended
        self.assertEqual(receiver_block1.signal_cache,
                         receiver_block2.signal_cache)

        # assert that original signals were sent
        self.assertEqual(receiver_block1.signal_cache,
                         signals)

        block_router.do_stop()
