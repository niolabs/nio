from unittest.mock import patch

from nio.block.base import Block
from nio.block.context import BlockContext
from nio.block.terminals import DEFAULT_TERMINAL
from nio.router.base import BlockRouter
from nio.router.context import RouterContext
from nio.service.base import BlockExecution
from nio.signal.base import Signal
from nio.testing.test_case import NIOTestCase


class SenderBlock(Block):

    def __init__(self):
        super().__init__()
        self.id = "sender_block"


class ReceiverBlock(Block):

    def __init__(self):
        super().__init__()
        self.id = "receiver_block"


class BlockExecutionTest(BlockExecution):

    def __init__(self, id, receivers):
        self.id = id
        self.receivers = receivers


class TestSignalsArgument(NIOTestCase):

    def test_signals_argument_type_check(self):
        """Asserts that router handles the argument signals per specifications
        """

        sender_block = SenderBlock()
        receiver_block = ReceiverBlock()
        block_router = BlockRouter()
        context = BlockContext(block_router, dict())
        blocks = {
            receiver_block.id():receiver_block,
            sender_block.id():sender_block
        }
        execution = [BlockExecutionTest(id=sender_block.id(),
                                        receivers=[receiver_block.id()])]
        router_context = RouterContext(execution, blocks)
        block_router.do_configure(router_context)
        block_router.do_start()

        sender_block.do_configure(context)

        with patch.object(receiver_block, 'process_signals') as receiver:
            signals = [Signal({"key": "val"})]
            sender_block.notify_signals(signals)
            receiver.assert_called_once_with(signals, DEFAULT_TERMINAL)

        # test sending more than one Signal
        with patch.object(receiver_block, 'process_signals') as receiver:
            signals = [Signal(), Signal()]
            sender_block.notify_signals(signals)
            receiver.assert_called_once_with(signals, DEFAULT_TERMINAL)

        # assert that sending signals as a set is allowed
        signals = set()
        signals.add(Signal())
        signals.add(Signal())
        with patch.object(receiver_block, 'process_signals') as receiver:
            sender_block.notify_signals(signals)
            receiver.assert_called_once_with(signals, DEFAULT_TERMINAL)

        # a list containing a dictionary raises TypeError
        dict_signal = {"key": "val"}
        with self.assertRaises(TypeError):
            sender_block.notify_signals([dict_signal])

        # test that an empty list is discarded
        with patch.object(receiver_block, 'process_signals') as receiver:
            sender_block.notify_signals([])
            self.assertEqual(receiver.call_count, 0)

        # test that all items in a list need to be a Signal instance
        with self.assertRaises(TypeError):
            sender_block.notify_signals([Signal(), object(), Signal()])

        block_router.do_stop()

    def test_signals_argument_no_type_check(self):
        """Asserts that router handles the argument signals per specifications
        """

        sender_block = SenderBlock()
        receiver_block = ReceiverBlock()
        block_router = BlockRouter()
        context = BlockContext(block_router, dict())
        blocks = {
            receiver_block.id():receiver_block,
            sender_block.id():sender_block
        }
        execution = [BlockExecutionTest(id=sender_block.id(),
                                        receivers=[receiver_block.id()])]
        router_context = RouterContext(execution, blocks,
                                       {"check_signal_type": False})
        block_router.do_configure(router_context)
        block_router.do_start()

        sender_block.do_configure(context)

        # a list containing a dictionary passes when not checking the types
        with patch.object(receiver_block, 'process_signals') as receiver:
            signals = [{"key": "val"}]
            sender_block.notify_signals(signals)
            receiver.assert_called_once_with(signals, DEFAULT_TERMINAL)

        # test that type of items in a list does not have to be Signal
        with patch.object(receiver_block, 'process_signals') as receiver:
            signals = [Signal(), object(), Signal()]
            sender_block.notify_signals(signals)
            receiver.assert_called_once_with(signals, DEFAULT_TERMINAL)

        block_router.do_stop()
