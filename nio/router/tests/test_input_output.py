from nio import Signal
from nio.block.base import Block
from nio.block.context import BlockContext
from nio.block.terminals import input, output, DEFAULT_TERMINAL
from nio.router.base import BlockRouter, BlockReceiverData, \
    InvalidProcessSignalsSignature, InvalidBlockOutput
from nio.router.context import RouterContext
from nio.service.base import BlockExecution
from nio.testing.test_case import NIOTestCase

# CONFIGURATION to follow for unittests understanding
"""
{
    # NOTE: this is not a complete config file but just has some ideas.
    "auto_start": false,
    "execution": [
        {
            "name": "log1",
            "receivers": []
        },
        {
            "name": "log2",
            "receivers": []
        },
        {
            # this is the normal, existing config.
            # note that receivers is a list.
            # state's default output goes to default input of log1.
            "name": "state",
            "receivers": [
                "log1"
            ]
        },
        {
            # a service with one output but a receiver with two inputs.
            # note that receivers is a list.
            # sim's default output goes to input 0 of state.
            # sim's default output also goes to input 1 of state.
            "name": "sim",
            "receivers": [
                {“name”: state", “input”: 0}, {“name”: “state", “input”: 1}
            ]
        },
        {
            # a service with two outputs.
            # output 0 goes to log1.
            # output 1 goes to log2.
            # note that receivers is a dict when the block has multiple inputs.
            "name": "two_outputs",
            "receivers": {
                0: ["log1"],
                1: ["log2"]
            }
        },



        {
            # a block with three outputs.
            # output 0 goes to input 0 of state.
            # output 0 goes to default input of log1.
            # output 1 goes to input 1 of state.
            # output 2 goes to default input of log2.
            "name": "three_outputs",
            "receivers": {
                0: [{“name”: "state", “input”: 0}, "log1"],
                1: [{“name”: "state", “input”: 1}],
                2: ["log2"]
            }
        }
        {
            # a service with two outputs, but had one before it was updated.
            # log2 should receive only output OLD.
            "name": "updated_block",
            "receivers": [
                "log2"
            ]
        }

    ],
    "log_level": "ERROR",
    "mappings": [],
    "name": "log",
    "status": "stopped",
    "type": "Service"
}

"""


class Sim(Block):

    def __init__(self):
        super().__init__()
        self.id = self.__class__.__name__.lower()

    def process_signals(self, signals, input_id=DEFAULT_TERMINAL):
        self.notify_signals(signals)


class Log1(Block):

    def __init__(self):
        super().__init__()
        self.id = self.__class__.__name__.lower()
        self.signal_cache = []

    def process_signals(self, signals, input_id=DEFAULT_TERMINAL):
        self.signal_cache.append(signals)


class Log2(Block):

    def __init__(self):
        super().__init__()
        self.id = self.__class__.__name__.lower()
        self.signal_cache = []

    # Don't have to define an input_id
    def process_signals(self, signals):
        self.signal_cache.append(signals)


class InvalidProcessSignals(Block):

    def __init__(self):
        super().__init__()
        self.id = self.__class__.__name__.lower()

    # This process signals signature is invalid and should throw an exception
    def process_signals(self, signals, input_id, what_am_i):
        pass


@output(0)
@output(1)
class Two_Outputs(Block):

    def __init__(self):
        super().__init__()
        self.id = self.__class__.__name__.lower()


@output(0)
@output(1)
@output(2)
class Three_Outputs(Block):

    def __init__(self):
        super().__init__()
        self.id = self.__class__.__name__.lower()


@input(0)
@input(1)
class State(Block):
    def __init__(self):
        super().__init__()
        self.id = self.__class__.__name__.lower()
        self.signal_cache_input0 = []
        self.signal_cache_input1 = []

    def process_signals(self, signals, input_id=DEFAULT_TERMINAL):
        if input_id == 0:
            self.signal_cache_input0.append(signals)
        else:
            self.signal_cache_input1.append(signals)


class BlockExecutionTest(BlockExecution):
    def __init__(self, id, receivers):
        self.id = id
        self.receivers = receivers


class TestInputOutput(NIOTestCase):

    def test_two_outputs_default_input(self):
        block_router = BlockRouter()
        context = BlockContext(block_router, dict())

        # create blocks
        two_outputs = Two_Outputs()
        two_outputs.configure(context)
        log1 = Log1()
        log1.configure(context)
        log2 = Log2()
        log2.configure(context)

        # create context initialization data
        blocks = {
            log1.id(): log1,
            log2.id(): log2,
            two_outputs.id(): two_outputs
        }

        input_id1 = 0
        input_id2 = 1
        execution = [
            BlockExecutionTest(id=two_outputs.id(),
                               receivers={0: [log1.id()],
                                          1: [log2.id()]})]

        router_context = RouterContext(execution, blocks,
                                       settings={"clone_signals": False})

        block_router.do_configure(router_context)
        block_router.do_start()

        signals = [Signal({"1": 1}),
                   Signal({"2": 2}),
                   Signal({"3": 3}),
                   Signal({"4": 4})]

        # make sure nothing has been delivered
        self.assertEqual(len(log1.signal_cache), 0)
        self.assertEqual(len(log2.signal_cache), 0)

        # when sending using input_id1, only block1 should receive
        two_outputs.notify_signals(signals, input_id1)
        # checking results
        self.assertEqual(len(log1.signal_cache), 1)
        self.assertIn(signals, log1.signal_cache)
        self.assertEqual(len(log2.signal_cache), 0)
        # clean up
        log1.signal_cache.remove(signals)

        # when sending using input_id2, only block2 should receive
        two_outputs.notify_signals(signals, input_id2)
        # checking results
        self.assertEqual(len(log1.signal_cache), 0)
        self.assertEqual(len(log2.signal_cache), 1)
        self.assertIn(signals, log2.signal_cache)
        # clean up
        log2.signal_cache.remove(signals)

        block_router.do_stop()

    def test_two_outputs_none_specified(self):
        """ This test verifies that it is possible to configure a router
        that uses a simple list receiver specification for a sending block
        with no default output when such receiver list is empty
        """
        block_router = BlockRouter()
        context = BlockContext(block_router, dict())

        # create blocks
        two_outputs = Two_Outputs()
        two_outputs.configure(context)
        log1 = Log1()
        log1.configure(context)

        # create context initialization data
        blocks = {
            log1.id(): log1,
            two_outputs.id(): two_outputs
        }
        execution = [
            BlockExecutionTest(id=two_outputs.id(),
                               receivers=[])]

        router_context = RouterContext(execution, blocks,
                                       settings={"clone_signals": False})

        # make sure configure does not raise exception
        block_router.do_configure(router_context)

    def test_two_outputs_list_specified(self):
        """ This test verifies that router fails to configure when block uses
        a simple list receiver specification for a sending block
        with no default output and receiver list is not empty
        """
        block_router = BlockRouter()
        context = BlockContext(block_router, dict())

        # create blocks
        two_outputs = Two_Outputs()
        two_outputs.configure(context)
        log1 = Log1()
        log1.configure(context)

        # create context initialization data
        blocks = {
            log1.id(): log1,
            two_outputs.id(): two_outputs
        }
        execution = [
            BlockExecutionTest(id=two_outputs.id(),
                               receivers=[log1.id()])]

        router_context = RouterContext(execution, blocks,
                                       settings={"clone_signals": False})

        # it raises since Block defines its own outputs but no default
        # (when specifying receivers using list format, the block output
        # is mandatory)
        with self.assertRaises(InvalidBlockOutput):
            block_router.do_configure(router_context)

    def test_three_outputs_mix_inputs(self):
        block_router = BlockRouter()
        context = BlockContext(block_router, dict())

        # create blocks
        three_outputs = Three_Outputs()
        three_outputs.configure(context)
        state = State()
        state.configure(context)
        log1 = Log1()
        log1.configure(context)
        log2 = Log2()
        log2.configure(context)

        # create context initialization data
        blocks = {
            log1.id(): log1,
            log2.id(): log2,
            state.id(): state,
            three_outputs.id(): three_outputs
        }
        input_id0 = 0
        input_id1 = 1
        input_id2 = 2
        execution = [BlockExecutionTest(
            id=three_outputs.id(),
            receivers={0: [{"id": state.id(), "input": input_id0}, log1.id()],
                       1: [{"id": state.id(), "input": input_id1}],
                       2: [log2.id()]})]

        router_context = RouterContext(execution, blocks,
                                       settings={"clone_signals": False})

        block_router.do_configure(router_context)
        block_router.do_start()

        signals = [Signal({"1": 1}),
                   Signal({"2": 2}),
                   Signal({"3": 3}),
                   Signal({"4": 4})]

        # make sure nothing has been delivered
        self.assertEqual(len(state.signal_cache_input0), 0)
        self.assertEqual(len(state.signal_cache_input1), 0)
        self.assertEqual(len(log1.signal_cache), 0)
        self.assertEqual(len(log2.signal_cache), 0)

        # when sending using input_id0, only input0 and log1 receive
        three_outputs.notify_signals(signals, input_id0)
        # checking results
        self.assertEqual(len(state.signal_cache_input0), 1)
        self.assertIn(signals, state.signal_cache_input0)
        self.assertEqual(len(state.signal_cache_input1), 0)
        self.assertEqual(len(log1.signal_cache), 1)
        self.assertIn(signals, log1.signal_cache)
        self.assertEqual(len(log2.signal_cache), 0)
        # clean up
        state.signal_cache_input0.remove(signals)
        log1.signal_cache.remove(signals)

        # when sending using input_id1, only input1 receives
        three_outputs.notify_signals(signals, input_id1)
        # checking results
        self.assertEqual(len(state.signal_cache_input0), 0)
        self.assertEqual(len(state.signal_cache_input1), 1)
        self.assertEqual(len(log1.signal_cache), 0)
        self.assertEqual(len(log2.signal_cache), 0)
        # clean up
        state.signal_cache_input1.remove(signals)

        # when sending using input_id2, only log2 receives
        three_outputs.notify_signals(signals, input_id2)
        # checking results
        self.assertEqual(len(state.signal_cache_input0), 0)
        self.assertEqual(len(state.signal_cache_input1), 0)
        self.assertEqual(len(log1.signal_cache), 0)
        self.assertEqual(len(log2.signal_cache), 1)

        block_router.do_stop()

    def test_input_id_required(self):
        """ Assert that different process_signals signatures are supported """
        # If the block defines input_id in process_signals (like Log1 does),
        # then our include_input_id attribute should be true
        with_input_id = BlockReceiverData(Log1(), 'input', 'output')
        self.assertTrue(with_input_id.include_input_id)

        # If the block does not define input_id in process_signals (like Log2),
        # then our include_input_id attribute should be false
        without_input_id = BlockReceiverData(Log2(), 'input', 'output')
        self.assertFalse(without_input_id.include_input_id)

        # We shouldn't be able to create block receiver data for a block
        # with an invalid process_signals signature
        with self.assertRaises(InvalidProcessSignalsSignature):
            BlockReceiverData(InvalidProcessSignals(), 'input', 'output')
