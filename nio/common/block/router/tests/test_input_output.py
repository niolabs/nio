import unittest
from nio.block.terminals import input, output
from nio.block.base import Block
from nio.block.context import BlockContext
from nio.common.block.router.base import BaseBlockRouter
from nio.common.block.controller import BlockController
from nio.common.block.router.context import RouterContext
from nio.util.support.test_case import NIOTestCaseNoModules

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
        self.name = self.__class__.__name__.lower()

    def process_signals(self, signals):
        self.notify_signals(signals)


class Log1(Block):

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__.lower()
        self.signal_cache = []

    def process_signals(self, signals):
        self.signal_cache.append(signals)


class Log2(Block):

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__.lower()
        self.signal_cache = []

    def process_signals(self, signals):
        self.signal_cache.append(signals)


@output(0)
@output(1)
class Two_Outputs(Block):

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__.lower()


@output(0)
@output(1)
@output(2)
class Three_Outputs(Block):

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__.lower()


@input(0)
@input(1)
class State(Block):

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__.lower()
        self.signal_cache_input0 = []
        self.signal_cache_input1 = []

    def process_signals(self, signals, input_id='default'):
        if input_id == 0:
            self.signal_cache_input0.append(signals)
        else:
            self.signal_cache_input1.append(signals)


class TestBlockExecution(object):

    def __init__(self, name, receivers):
        self.name = name
        self.receivers = receivers


class TestInputOutput(NIOTestCaseNoModules):

    @unittest.skip('use to satisfy behavior before 03172015 changes')
    def test_default_output_two_inputs(self):
        block_router = BaseBlockRouter()
        context = BlockContext(block_router, dict(), dict(), None)

        # create blocks
        sim = BlockController(Sim)
        sim.configure(context)
        state = BlockController(State)
        state.configure(context)

        # create context initialization data
        blocks = dict(state=state, sim=sim)

        input_id0 = 0
        input_id1 = 1
        execution = [
            TestBlockExecution(name="sim",
                               receivers=[
                                   {"name": "state",
                                    "input": input_id0},
                                   {"name": "state",
                                    "input": input_id1}])]

        router_context = RouterContext(execution, blocks)

        block_router.configure(router_context)
        block_router.start()

        signals = [1, 2, 3, 4]

        # make sure nothing has been delivered
        self.assertEqual(len(state.block.signal_cache_input0), 0)
        self.assertEqual(len(state.block.signal_cache_input1), 0)

        # when sending using input_id1, only input1 should receive
        sim.block.notify_signals(signals, input_id0)

        # checking results
        self.assertIsNotNone(state.block.signal_cache_input0)
        self.assertIn(signals, state.block.signal_cache_input0)
        self.assertEqual(len(state.block.signal_cache_input1), 0)
        # clean up
        state.block.signal_cache_input0.remove(signals)
        # assert that it is clean again
        self.assertEqual(len(state.block.signal_cache_input0), 0)
        self.assertEqual(len(state.block.signal_cache_input1), 0)

        # when sending using input_id2, only input2 should receive
        sim.block.notify_signals(signals, input_id1)
        # checking results
        self.assertEqual(len(state.block.signal_cache_input0), 0)
        self.assertIn(signals, state.block.signal_cache_input1)

        block_router.stop()

    def test_two_outputs_default_input(self):
        block_router = BaseBlockRouter()
        context = BlockContext(block_router, dict(), dict(), None)

        # create blocks
        two_outputs = BlockController(Two_Outputs)
        two_outputs.configure(context)
        log1 = BlockController(Log1)
        log1.configure(context)
        log2 = BlockController(Log2)
        log2.configure(context)

        # create context initialization data
        blocks = dict(log1=log1,
                      log2=log2,
                      two_outputs=two_outputs)

        input_id1 = 0
        input_id2 = 1
        execution = [
            TestBlockExecution(name="two_outputs",
                               receivers={0: ["log1"],
                                          1: ["log2"]})]

        router_context = RouterContext(execution, blocks)

        block_router.configure(router_context)
        block_router.start()

        signals = [1, 2, 3, 4]

        # make sure nothing has been delivered
        self.assertEqual(len(log1.block.signal_cache), 0)
        self.assertEqual(len(log2.block.signal_cache), 0)

        # when sending using input_id1, only block1 should receive
        two_outputs.block.notify_signals(signals, input_id1)
        # checking results
        self.assertEqual(len(log1.block.signal_cache), 1)
        self.assertIn(signals, log1.block.signal_cache)
        self.assertEqual(len(log2.block.signal_cache), 0)
        # clean up
        log1.block.signal_cache.remove(signals)

        # when sending using input_id2, only block2 should receive
        two_outputs.block.notify_signals(signals, input_id2)
        # checking results
        self.assertEqual(len(log1.block.signal_cache), 0)
        self.assertEqual(len(log2.block.signal_cache), 1)
        self.assertIn(signals, log2.block.signal_cache)
        # clean up
        log2.block.signal_cache.remove(signals)

        block_router.stop()

    def test_three_outputs_mix_inputs(self):
        block_router = BaseBlockRouter()
        context = BlockContext(block_router, dict(), dict(), None)

        # create blocks
        three_outputs = BlockController(Three_Outputs)
        three_outputs.configure(context)
        state = BlockController(State)
        state.configure(context)
        log1 = BlockController(Log1)
        log1.configure(context)
        log2 = BlockController(Log2)
        log2.configure(context)

        # create context initialization data
        blocks = dict(three_outputs=three_outputs,
                      state=state,
                      log1=log1,
                      log2=log2)

        input_id0 = 0
        input_id1 = 1
        input_id2 = 2
        execution = [TestBlockExecution(
            name="three_outputs",
            receivers={0: [{"name": "state", "input": input_id0}, "log1"],
                       1: [{"name": "state", "input": input_id1}],
                       2: ["log2"]})]

        router_context = RouterContext(execution, blocks)

        block_router.configure(router_context)
        block_router.start()

        signals = [1, 2, 3, 4]

        # make sure nothing has been delivered
        self.assertEqual(len(state.block.signal_cache_input0), 0)
        self.assertEqual(len(state.block.signal_cache_input1), 0)
        self.assertEqual(len(log1.block.signal_cache), 0)
        self.assertEqual(len(log2.block.signal_cache), 0)

        # when sending using input_id0, only input0 and log1 receive
        three_outputs.block.notify_signals(signals, input_id0)
        # checking results
        self.assertEqual(len(state.block.signal_cache_input0), 1)
        self.assertIn(signals, state.block.signal_cache_input0)
        self.assertEqual(len(state.block.signal_cache_input1), 0)
        self.assertEqual(len(log1.block.signal_cache), 1)
        self.assertIn(signals, log1.block.signal_cache)
        self.assertEqual(len(log2.block.signal_cache), 0)
        # clean up
        state.block.signal_cache_input0.remove(signals)
        log1.block.signal_cache.remove(signals)

        # when sending using input_id1, only input1 receives
        three_outputs.block.notify_signals(signals, input_id1)
        # checking results
        self.assertEqual(len(state.block.signal_cache_input0), 0)
        self.assertEqual(len(state.block.signal_cache_input1), 1)
        self.assertEqual(len(log1.block.signal_cache), 0)
        self.assertEqual(len(log2.block.signal_cache), 0)
        # clean up
        state.block.signal_cache_input1.remove(signals)

        # when sending using input_id2, only log2 receives
        three_outputs.block.notify_signals(signals, input_id2)
        # checking results
        self.assertEqual(len(state.block.signal_cache_input0), 0)
        self.assertEqual(len(state.block.signal_cache_input1), 0)
        self.assertEqual(len(log1.block.signal_cache), 0)
        self.assertEqual(len(log2.block.signal_cache), 1)

        block_router.stop()
