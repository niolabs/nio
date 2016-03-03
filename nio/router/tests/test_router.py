from collections import defaultdict
from unittest.mock import patch

from nio.block.base import Block
from nio.block.context import BlockContext
from nio.block.terminals import input, output, DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.router.context import RouterContext
from nio.router.base import BlockRouter, InvalidBlockOutput, \
    InvalidBlockInput, MissingBlock, BlockRouterNotStarted
from nio.service.base import BlockExecution
from nio.util.runner import RunnerStatus
from nio.util.support.test_case import NIOTestCaseNoModules


class TestBaseRouter(NIOTestCaseNoModules):

    def _configure_router(self, block_1, block_2, block_1_output=None,
                          block_2_input=None):
        """ Create a block router given a certain execution configuration.

        This test helper method takes two block classes and connects them
        together in a block router. If outputs or inputs are included, the
        connection happens including that information. If not included, the
        block's default inputs and outputs will be used.

        Returns:
            tuple of (block1, block2)

        Examples:

        _configure_router(Block1, Block2)
            +-----------+
            |           |
            |  Block_1  |
            |           |
            +-----+-----+
                  |
            +-----v-----+
            |           |
            |  Block 2  |
            |           |
            +-----------+


        _configure_router(Block1, Block2, "one")
            +-----------+
            |           |
            |  Block 1  |
            |           |
            | one   two |
            +--+--------+
               |
               +--+
                  |
            +-----v-----+
            |           |
            |  Block 2  |
            |           |
            +-----------+

        _configure_router(Block1, Block2, None, "two")
            +-----------+
            |           |
            |  Block 1  |
            |           |
            +-----+-----+
                  |
                  +--+
                     |
            +--------v--+
            | one   two |
            |           |
            |  Block 2  |
            |           |
            +-----------+


        _configure_router(Block1, Block2, "one", "two")
            +-----------+
            |           |
            |  Block 1  |
            |           |
            | one   two |
            +--+--------+
               |
               +-----+
                     |
            +--------v--+
            | one   two |
            |           |
            |  Block 2  |
            |           |
            +-----------+
        """
        router = BlockRouter()
        context = BlockContext(router, {})
        b1 = block_1()
        b1.name = "b1"
        b1.configure(context)
        b2 = block_2()
        b2.name = "b2"
        b2.configure(context)

        blocks = {
            "b1": b1,
            "b2": b2
        }

        b1_execution = BlockExecution()
        b1_execution.name = "b1"

        if block_1_output is None and block_2_input is None:
            # Both default terminals
            # Just specify the name of the block for receiver
            b1_execution.receivers = ["b2"]
        elif block_1_output is None and block_2_input is not None:
            # Default output, specified input
            # Specify a dict for receiver containing input and block name
            b1_execution.receivers = [{
                "name": "b2",
                "input": block_2_input
            }]
        elif block_1_output is not None and block_2_input is None:
            # Specified output, default input
            # Source block is a dict with output, receiver is block name
            b1_execution.receivers = {
                block_1_output: ["b2"]
            }
        elif block_1_output is not None and block_2_input is not None:
            # Specified output, specified input
            # Source block is a dict with output, receiver is dict with input
            b1_execution.receivers = {
                block_1_output: [{
                    "name": "b2",
                    "input": block_2_input
                }]
            }

        router_context = RouterContext([b1_execution], blocks)
        router.do_configure(router_context)

        return b1, b2, router

    def test_default_out_default_in(self):
        """ Test default output to default input """

        # No overriding of any inputs/outputs, use base block default
        class SourceBlock(RouterTestBlock):
            pass

        # No overriding of any inputs/outputs, use base block default
        class DestBlock(RouterTestBlock):
            pass

        source, dest, router = self._configure_router(SourceBlock, DestBlock)

        router.do_start()
        # Notify a signal from the default output
        source.notify_signals([Signal()])
        # Should have 1 and only 1 signals on the default input
        self.assertEqual(dest.total_signals_received, 1)
        self.assertEqual(len(dest.signals_received[DEFAULT_TERMINAL]), 1)
        router.do_stop()

    def test_default_out_specified_in(self):
        """ Test default output to specified input """

        # No overriding of any inputs/outputs, use base block default
        class SourceBlock(RouterTestBlock):
            pass

        @input("test_input")
        class DestBlock(RouterTestBlock):
            pass

        source, dest, router = self._configure_router(
            SourceBlock, DestBlock, None, "test_input")

        router.do_start()
        # Notify a signal from the default output
        source.notify_signals([Signal()])
        # Should have 1 and only 1 signals on the specified input
        self.assertEqual(dest.total_signals_received, 1)
        self.assertEqual(len(dest.signals_received[DEFAULT_TERMINAL]), 0)
        self.assertEqual(len(dest.signals_received["test_input"]), 1)
        router.do_stop()

    def test_specified_out_default_in(self):
        """ Test default output to specified input """

        @output("test_output")
        class SourceBlock(RouterTestBlock):
            pass

        # No overriding of any inputs/outputs, use base block default
        class DestBlock(RouterTestBlock):
            pass

        source, dest, router = self._configure_router(
            SourceBlock, DestBlock, "test_output", None)

        # Cannot configure a router with default outputs if the block
        # doesn't declare a default output
        with self.assertRaises(InvalidBlockOutput):
            self._configure_router(SourceBlock, DestBlock, None, None)

        router.do_start()
        # Notify a signal from the specified output
        source.notify_signals([Signal()], "test_output")
        # Should have 1 and only 1 signals on the default input
        self.assertEqual(dest.total_signals_received, 1)
        self.assertEqual(len(dest.signals_received[DEFAULT_TERMINAL]), 1)
        router.do_stop()

    def test_specified_out_specified_in(self):
        """ Test specified output to specified input """

        @output("test_output")
        class SourceBlock(RouterTestBlock):
            pass

        @input("test_input")
        class DestBlock(RouterTestBlock):
            pass

        source, dest, router = self._configure_router(
            SourceBlock, DestBlock, "test_output", "test_input")

        router.do_start()
        # Notify a signal from the specified output
        source.notify_signals([Signal()], "test_output")
        # Should have 1 and only 1 signals on the specified input
        self.assertEqual(dest.total_signals_received, 1)
        self.assertEqual(len(dest.signals_received[DEFAULT_TERMINAL]), 0)
        self.assertEqual(len(dest.signals_received["test_input"]), 1)
        router.do_stop()

    def test_invalid_out_invalid_in(self):
        """ Test block router with invalid inputs/outputs """

        @output("test_output")
        class SourceBlock(RouterTestBlock):
            pass

        @input("test_input")
        class DestBlock(RouterTestBlock):
            pass

        # Shouldn't even be able to configure the block router if the input
        # or output don't exist
        with self.assertRaises(InvalidBlockOutput):
            self._configure_router(
                SourceBlock, DestBlock, "invalid_output", "test_input")
        with self.assertRaises(InvalidBlockInput):
            self._configure_router(
                SourceBlock, DestBlock, "test_output", "invalid_input")
        # Configuring a router without a terminal id when there is no default
        # raises an exception too
        with self.assertRaises(InvalidBlockInput):
            self._configure_router(
                SourceBlock, DestBlock, "test_output", None)
        with self.assertRaises(InvalidBlockOutput):
            self._configure_router(
                SourceBlock, DestBlock, None, "test_input")

    def test_notify_from_invalid_output(self):
        """ Test a block can't notify from an output that doesn't exist """

        @output("test_output")
        class SourceBlock(RouterTestBlock):
            pass

        @input("test_input")
        class DestBlock(RouterTestBlock):
            pass

        source, dest, router = self._configure_router(
            SourceBlock, DestBlock, "test_output", "test_input")

        router.do_start()
        # Notify a signal from the default output
        with self.assertRaises(InvalidBlockOutput):
            source.notify_signals([Signal()])
        # Notify a signal from a non-existent output
        with self.assertRaises(InvalidBlockOutput):
            source.notify_signals([Signal()], "invalid_output")
        router.do_stop()

    def test_overridden_out_overridden_in(self):
        """ Test blocks can override default inputs/outputs and still route """

        @output("test_output_2", default=True)
        @output("test_output_1")
        class SourceBlock(RouterTestBlock):
            pass

        @input("test_input_2", default=True)
        @input("test_input_1")
        class DestBlock(RouterTestBlock):
            pass

        # Configure the router to use both defaults
        source, dest, router = self._configure_router(
            SourceBlock, DestBlock, None, None)

        router.do_start()
        # Notify a signal from the default output
        source.notify_signals([Signal()])
        # Should have 1 and only 1 signals on the specified input
        self.assertEqual(dest.total_signals_received, 1)
        self.assertEqual(len(dest.signals_received[DEFAULT_TERMINAL]), 0)
        self.assertEqual(len(dest.signals_received["test_input_1"]), 0)
        self.assertEqual(len(dest.signals_received["test_input_2"]), 1)

        # Notify a signal from the specified default output
        source.notify_signals([Signal()], "test_output_2")
        # Should have 2 signals there now
        self.assertEqual(dest.total_signals_received, 2)
        self.assertEqual(len(dest.signals_received[DEFAULT_TERMINAL]), 0)
        self.assertEqual(len(dest.signals_received["test_input_1"]), 0)
        self.assertEqual(len(dest.signals_received["test_input_2"]), 2)
        router.do_stop()

    def test_invalid_signals(self):
        """ Test router only accepts a signals iterable """

        class SourceBlock(Block):
            pass

        class DestBlock(Block):
            pass

        source, dest, router = self._configure_router(
            SourceBlock, DestBlock)

        router.do_start()
        # Notify invalid signal
        with self.assertRaises(TypeError):
            router.notify_signals(source, Signal(), DEFAULT_TERMINAL)
        router.do_stop()

    def test_receiver_missing_block(self):
        """ Validates execution receiver block """

        class SourceBlock(Block):
            pass

        class DestBlock(Block):
            pass

        router = BlockRouter()
        context = BlockContext(router, {})
        source = SourceBlock()
        source.name = "source"
        source.configure(context)
        dest = DestBlock()
        dest.name = "dest"
        dest.configure(context)

        blocks = {
            "source": source,
            "dest": dest
        }

        source_execution = BlockExecution()
        source_execution.name = "source"
        # block receiver name is invalid, it expects a valid block name
        source_execution.receivers = ["invalid"]

        router_context = RouterContext([source_execution], blocks)
        with self.assertRaises(MissingBlock):
            router.do_configure(router_context)

    def test_receiver_invalid_format(self):
        """ Test receiver format validity """

        class SourceBlock(Block):
            pass

        class DestBlock(Block):
            pass

        router = BlockRouter()
        context = BlockContext(router, {})
        source = SourceBlock()
        source.name = "source"
        source.configure(context)
        dest = DestBlock()
        dest.name = "dest"
        dest.configure(context)

        blocks = {
            "source": source,
            "dest": dest
        }

        source_execution = BlockExecution()
        source_execution.name = "source"
        # make receivers format invalid
        source_execution.receivers = [{
            "input": DEFAULT_TERMINAL,
            "invalid": "invalid"
        }]

        router_context = RouterContext([source_execution], blocks)
        with self.assertRaises(KeyError):
            router.do_configure(router_context)

        # make block name invalid to cause a MissingBlock
        source_execution.receivers = [{
            "input": DEFAULT_TERMINAL,
            "name": "invalid"
        }]
        router_context = RouterContext([source_execution], blocks)
        with self.assertRaises(MissingBlock):
            router.do_configure(router_context)

    def test_sending_from_block_in_warning_error(self):
        """ Asserts that router does not route signals to a block in error
        status, but does when block is in warning status
        """

        class SourceBlock(RouterTestBlock):
            pass

        class DestBlock(RouterTestBlock):
            pass

        source, dest, router = self._configure_router(
            SourceBlock, DestBlock)

        # set dest block status to error
        dest.status = RunnerStatus.error

        router.do_start()
        # Notify signal
        self.assertEqual(dest.total_signals_received, 0)
        router.notify_signals(source, [Signal()], DEFAULT_TERMINAL)
        # assert that no signals were delivered since block was in error
        self.assertEqual(dest.total_signals_received, 0)

        # set dest block status to warning
        dest.status = RunnerStatus.warning
        router.notify_signals(source, [Signal()], DEFAULT_TERMINAL)
        # assert that signals were delivered when in warning
        self.assertEqual(dest.total_signals_received, 1)

        router.do_stop()

    def test_sending_router_status_changes(self):
        """ Asserts signals delivery depending on router status """

        class SourceBlock(RouterTestBlock):
            pass

        class DestBlock(RouterTestBlock):
            pass

        source, dest, router = self._configure_router(
            SourceBlock, DestBlock)

        self.assertEqual(dest.total_signals_received, 0)
        with self.assertRaises(BlockRouterNotStarted):
            router.notify_signals(source, [Signal()], DEFAULT_TERMINAL)
        self.assertEqual(dest.total_signals_received, 0)

        router.do_start()
        # Notify signal
        self.assertEqual(dest.total_signals_received, 0)
        router.notify_signals(source, [Signal()], DEFAULT_TERMINAL)
        self.assertEqual(dest.total_signals_received, 1)

        router.status = RunnerStatus.stopping
        router.notify_signals(source, [Signal()], DEFAULT_TERMINAL)
        self.assertEqual(dest.total_signals_received, 1)

        # force status back to started
        router.status = RunnerStatus.started

        router.notify_signals(source, [Signal()], DEFAULT_TERMINAL)
        # assert that signals were delivered again
        self.assertEqual(dest.total_signals_received, 2)

        router.do_stop()

        # after stopping router, no signals are delivered
        router.notify_signals(source, [Signal()], DEFAULT_TERMINAL)
        # assert that signals were delivered again
        self.assertEqual(dest.total_signals_received, 2)

    def test_cloning_error(self):
        """ Test router only accepts a signals iterable """

        class SourceBlock(RouterTestBlock):
            pass

        class DestBlock1(RouterTestBlock):
            pass

        class DestBlock2(RouterTestBlock):
            pass

        router = BlockRouter()
        context = BlockContext(router, {})
        source = SourceBlock()
        source.name = "source"
        source.configure(context)

        dest1 = DestBlock1()
        dest1.name = "dest1"
        dest1.configure(context)

        dest2 = DestBlock2()
        dest2.name = "dest2"
        dest2.configure(context)

        blocks = {
            "source": source,
            "dest1": dest1,
            "dest2": dest2
        }

        source_execution = BlockExecution()
        source_execution.name = "source"
        source_execution.receivers = ["dest1", "dest2"]

        router_context = RouterContext([source_execution], blocks,
                                       settings={"clone_signals": True})
        router.do_configure(router_context)

        router.do_start()
        # Notify signal
        self.assertEqual(dest1.total_signals_received, 0)
        self.assertEqual(dest2.total_signals_received, 0)
        signals = [Signal()]
        router.notify_signals(source, signals, DEFAULT_TERMINAL)
        # assert that signals were delivered
        self.assertEqual(dest1.total_signals_received, 1)
        self.assertEqual(dest2.total_signals_received, 1)
        # assert that signals were deep-copied
        self.assertNotEqual(dest1.signals_received[DEFAULT_TERMINAL], signals)
        self.assertNotEqual(dest2.signals_received[DEFAULT_TERMINAL], signals)

        # clear out signal reception
        dest1.total_signals_received = 0
        dest1.signals_received[DEFAULT_TERMINAL] = []
        dest2.total_signals_received = 0
        dest2.signals_received[DEFAULT_TERMINAL] = []

        with patch('nio.router.base.deepcopy') as patched_deepcopy:
            patched_deepcopy.side_effect = RuntimeError()

            router.notify_signals(source, signals, DEFAULT_TERMINAL)
            # assert that signals were delivered
            self.assertEqual(dest1.total_signals_received, 1)
            self.assertEqual(dest2.total_signals_received, 1)
            # assert that signals were NOT deep-copied
            self.assertEqual(dest1.signals_received[DEFAULT_TERMINAL], signals)
            self.assertEqual(dest2.signals_received[DEFAULT_TERMINAL], signals)


class RouterTestBlock(Block):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.total_signals_received = 0
        self.signals_received = defaultdict(list)

    def process_signals(self, signals, input_id):
        self.total_signals_received += len(signals)
        self.signals_received[input_id].extend(signals)
