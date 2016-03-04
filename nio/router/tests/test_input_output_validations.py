from nio import Signal
from nio.block.base import Block
from nio.block.context import BlockContext
from nio.router.base import BlockRouter, InvalidBlockOutput, \
    InvalidBlockInput
from nio.router.context import RouterContext
from nio.service.base import BlockExecution
from nio.testing.test_case import NIOTestCaseNoModules
from nio.block.terminals import input, output, DEFAULT_TERMINAL


class OutputBlock(Block):

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__.lower()


@output("first", default=True)
class FirstOutputBlock(OutputBlock):
    pass


@output("second", default=True)
class SecondOutputBlock(Block):
    pass


class InputBlock(Block):

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__.lower()
        self.signal_cache = []

    def process_signals(self, signals, input_id=DEFAULT_TERMINAL):
        self.signal_cache.append(signals)


@input("first", default=True)
class FirstInputBlock(InputBlock):
    pass


@input("second", default=True)
class SecondInputBlock(InputBlock):
    pass


class BlockExecutionTest(BlockExecution):

    def __init__(self, name, receivers):
        self.name = name
        self.receivers = receivers


class TestInputOutputValidations(NIOTestCaseNoModules):

    def test_valid_input_output(self):
        block_router = BlockRouter()
        context = BlockContext(block_router, dict())

        # create blocks
        sender_block = FirstOutputBlock()
        sender_block.configure(context)
        receiver_block = FirstInputBlock()
        receiver_block.configure(context)

        # create context initialization data
        blocks = dict(firstinputblock=receiver_block,
                      firstoutputblock=sender_block)

        input_id1 = "first"
        execution = [
            BlockExecutionTest(
                name="FirstOutputBlock".lower(),
                receivers={
                    "first": [
                        "FirstInputBlock".lower()]})]

        router_context = RouterContext(execution, blocks)

        block_router.do_configure(router_context)
        block_router.do_start()

        signals = [Signal({"1": 1}),
                   Signal({"2": 2}),
                   Signal({"3": 3}),
                   Signal({"4": 4})]

        # make sure nothing has been delivered
        self.assertEqual(len(receiver_block.signal_cache), 0)

        sender_block.notify_signals(signals, input_id1)

        # checking results
        self.assertIn(signals, receiver_block.signal_cache)
        # clean up
        receiver_block.signal_cache.remove(signals)

        block_router.do_stop()

    def test_valid_input_invalid_output(self):
        block_router = BlockRouter()
        context = BlockContext(block_router, dict())

        # create blocks
        sender_block = FirstOutputBlock()
        sender_block.configure(context)
        receiver_block = FirstInputBlock()
        receiver_block.configure(context)

        # create context initialization data
        blocks = dict(firstinputblock=receiver_block,
                      firstoutputblock=sender_block)

        execution = [
            BlockExecutionTest(name="FirstOutputBlock".lower(),
                               receivers={"second": [
                                   {"name": "FirstInputBlock".lower(),
                                    "input": "first"}]})]
        router_context = RouterContext(execution, blocks)

        self.assertRaises(InvalidBlockOutput,
                          block_router.configure,
                          router_context)

    def test_invalid_input_valid_output2(self):
        block_router = BlockRouter()
        context = BlockContext(block_router, dict())

        # create blocks
        sender_block = FirstOutputBlock()
        sender_block.configure(context)
        receiver_block = SecondInputBlock()
        receiver_block.configure(context)

        # create context initialization data
        blocks = dict(secondinputblock=receiver_block,
                      firstoutputblock=sender_block)

        execution = [
            BlockExecutionTest(name="FirstOutputBlock".lower(),
                               receivers={"first": [
                                   {"name": "SecondInputBlock".lower(),
                                    "input": "first"}]})]
        router_context = RouterContext(execution, blocks)

        self.assertRaises(InvalidBlockInput,
                          block_router.configure,
                          router_context)

    def test_one_input_default_output(self):
        """ Asserts that data can be passed from a default output to 1 input

        OutputBlock has DEFAULT_TERMINAL since it inherits from Block and has
        no output definitions

        FirstInputBlock only input is 'first' yet it receives from 'default'
        """

        block_router = BlockRouter()
        context = BlockContext(block_router, dict())

        # create blocks
        sender_block = OutputBlock()
        sender_block.configure(context)
        receiver_block = FirstInputBlock()
        receiver_block.configure(context)

        # create context initialization data
        blocks = dict(firstinputblock=receiver_block,
                      outputblock=sender_block)

        execution = [
            BlockExecutionTest(name="OutputBlock".lower(),
                               receivers=["FirstInputBlock".lower()])]
        router_context = RouterContext(execution, blocks)

        block_router.do_configure(router_context)
        block_router.do_start()

        signals = [Signal({"1": 1}),
                   Signal({"2": 2}),
                   Signal({"3": 3}),
                   Signal({"4": 4})]

        # make sure nothing has been delivered
        self.assertEqual(len(receiver_block.signal_cache), 0)

        sender_block.notify_signals(signals)
        # checking results
        self.assertIn(signals, receiver_block.signal_cache)
        # clean up
        receiver_block.signal_cache.remove(signals)

        block_router.do_stop()
