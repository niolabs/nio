import unittest
from nio.common.block.base import Block
from nio.common.block.context import BlockContext
from nio.common.block.router.base import BaseBlockRouter, InvalidBlockOutput, \
    InvalidBlockInput
from nio.common.block.controller import BlockController
from nio.common.block.router.context import RouterContext
from nio.util.support.test_case import NIOTestCaseNoModules
from nio.common.block.attribute import Attribute


class OutputBlock(Block):

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__.lower()


@Attribute("output", "first")
class FirstOutputBlock(OutputBlock):
    pass


@Attribute("output", "second")
class SecondOutputBlock(Block):
    pass


class InputBlock(Block):

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__.lower()
        self.signal_cache = []

    def process_signals(self, signals, input_id='default'):
        self.signal_cache.append(signals)


@Attribute("input", "first")
class FirstInputBlock(InputBlock):
    pass


@Attribute("input", "second")
class SecondInputBlock(InputBlock):
    pass


class TestBlockExecution(object):

    def __init__(self, name, receivers):
        self.name = name
        self.receivers = receivers


class TestInputOutputValidations(NIOTestCaseNoModules):

    def test_valid_input_output(self):
        block_router = BaseBlockRouter()
        context = BlockContext(block_router, dict(), dict(), None)

        # create blocks
        sender_block = BlockController(FirstOutputBlock)
        sender_block.configure(context)
        receiver_block = BlockController(FirstInputBlock)
        receiver_block.configure(context)

        # create context initialization data
        blocks = dict(firstinputblock=receiver_block,
                      firstoutputblock=sender_block)

        input_id1 = "first"
        execution = [
            TestBlockExecution(
                name="FirstOutputBlock".lower(),
                receivers={
                    "first": [
                        "FirstInputBlock".lower()]})]

        router_context = RouterContext(execution, blocks)

        block_router.configure(router_context)
        block_router.start()

        signals = [1, 2, 3, 4]

        # make sure nothing has been delivered
        self.assertEqual(len(receiver_block.block.signal_cache), 0)

        sender_block.block.notify_signals(signals, input_id1)

        # checking results
        self.assertIn(signals, receiver_block.block.signal_cache)
        # clean up
        receiver_block.block.signal_cache.remove(signals)

        block_router.stop()

    def test_valid_input_invalid_output(self):
        block_router = BaseBlockRouter()
        context = BlockContext(block_router, dict(), dict(), None)

        # create blocks
        sender_block = BlockController(FirstOutputBlock)
        sender_block.configure(context)
        receiver_block = BlockController(FirstInputBlock)
        receiver_block.configure(context)

        # create context initialization data
        blocks = dict(firstinputblock=receiver_block,
                      firstoutputblock=sender_block)

        execution = [
            TestBlockExecution(name="FirstOutputBlock".lower(),
                               receivers={"second": [
                                   {"name": "FirstInputBlock".lower(),
                                    "input": "first"}]})]
        router_context = RouterContext(execution, blocks)

        self.assertRaises(InvalidBlockOutput,
                          block_router.configure,
                          router_context)

    @unittest.skip('old constraint no longer enforceable, 03172015 changes')
    def test_invalid_input_valid_output1(self):
        block_router = BaseBlockRouter()
        context = BlockContext(block_router, dict(), dict(), None)

        # create blocks
        sender_block = BlockController(FirstOutputBlock)
        sender_block.configure(context)
        receiver_block = BlockController(SecondInputBlock)
        receiver_block.configure(context)

        # create context initialization data
        blocks = dict(secondinputblock=receiver_block,
                      firstoutputblock=sender_block)

        execution = [
            TestBlockExecution(name="FirstOutputBlock".lower(),
                               receivers={"first": [
                                   {"name": "SecondInputBlock".lower(),
                                    "input": "second"}]})]
        router_context = RouterContext(execution, blocks)

        self.assertRaises(InvalidBlockInput,
                          block_router.configure,
                          router_context)

    def test_invalid_input_valid_output2(self):
        block_router = BaseBlockRouter()
        context = BlockContext(block_router, dict(), dict(), None)

        # create blocks
        sender_block = BlockController(FirstOutputBlock)
        sender_block.configure(context)
        receiver_block = BlockController(SecondInputBlock)
        receiver_block.configure(context)

        # create context initialization data
        blocks = dict(secondinputblock=receiver_block,
                      firstoutputblock=sender_block)

        execution = [
            TestBlockExecution(name="FirstOutputBlock".lower(),
                               receivers={"first": [
                                   {"name": "SecondInputBlock".lower(),
                                    "input": "first"}]})]
        router_context = RouterContext(execution, blocks)

        self.assertRaises(InvalidBlockInput,
                          block_router.configure,
                          router_context)

    def test_one_input_default_output(self):
        """ Asserts that data can be passed from a default output to a block
        that has one input overriding default using old receiver format

        OutputBlock has 'default' since it inherits from Block and has no
        output definitions

        FirstInputBlock only input is 'first' yet it receives from 'default'
        """

        block_router = BaseBlockRouter()
        context = BlockContext(block_router, dict(), dict(), None)

        # create blocks
        sender_block = BlockController(OutputBlock)
        sender_block.configure(context)
        receiver_block = BlockController(FirstInputBlock)
        receiver_block.configure(context)

        # create context initialization data
        blocks = dict(firstinputblock=receiver_block,
                      outputblock=sender_block)

        execution = [
            TestBlockExecution(name="OutputBlock".lower(),
                               receivers=["FirstInputBlock".lower()])]
        router_context = RouterContext(execution, blocks)

        block_router.configure(router_context)
        block_router.start()
        signals = [1, 2, 3, 4]

        # make sure nothing has been delivered
        self.assertEqual(len(receiver_block.block.signal_cache), 0)

        sender_block.block.notify_signals(signals, 'default')
        # checking results
        self.assertIn(signals, receiver_block.block.signal_cache)
        # clean up
        receiver_block.block.signal_cache.remove(signals)

        block_router.stop()
