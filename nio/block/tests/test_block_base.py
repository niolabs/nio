from unittest.mock import patch, Mock
from nio.block.base import Block
from nio.block.context import BlockContext
from nio.block.terminals import DEFAULT_TERMINAL
from nio.properties.exceptions import AllowNoneViolation
from nio.signal.base import Signal
from nio.router.base import BlockRouter
from nio.router.context import RouterContext
from nio.util.support.test_case import NIOTestCaseNoModules


class TestBaseBlock(NIOTestCaseNoModules):

    def test_configure(self):
        """Make sure a block can be configured"""
        blk = Block()
        blk.configure(BlockContext(
            BlockRouter(),
            {"name": "BlockName", "log_level": "WARNING"},
            {}))
        # Make sure the name property got set properly
        self.assertEqual(blk.name(), "BlockName")

    def test_invalid_configure(self):
        """Make sure a block is configured with valid information"""
        class JustAnObject(object):
            pass
        with self.assertRaises(TypeError):
            # Can't configure with a non BlockContext
            Block().configure(JustAnObject)
        with self.assertRaises(TypeError):
            # The context's block router needs to be a BlockRouter
            Block().configure(BlockContext(JustAnObject, {}))
        with self.assertRaises(AllowNoneViolation):
            # Block needs a name
            Block().configure(BlockContext(BlockRouter(), {"name": None}))
        with self.assertRaises(TypeError):
            # Wrong types (like log_level not being corrrect) raise TypeError
            Block().configure(BlockContext(BlockRouter(), {"name": "BlockName",
                                                           "log_level": 42}))

    def test_notify_management_signal(self):
        """Test the block can notify management signals properly to
        block router"""
        blk = Block()
        blk.configure(BlockContext(
            BlockRouter(),
            {"name": "BlockName", "log_level": "WARNING"},
            {}))
        my_sig = Signal({"key": "val"})
        with patch.object(blk, '_block_router') as router_patch:
            blk.notify_management_signal(my_sig)
            router_patch.notify_management_signal.assert_called_once_with(
                blk, my_sig)

    def test_service_notify_management_signal(self):
        """ Test the block can notify management signals properly by making it
        all the way to service mgmt handler """
        blk = Block()
        service_mgmt_signal_handler = Mock()
        block_router = BlockRouter()
        router_context = \
            RouterContext([], {},
                          mgmt_signal_handler=service_mgmt_signal_handler)
        block_router.configure(router_context)
        blk.configure(BlockContext(
            block_router,
            {"name": "BlockName", "log_level": "WARNING"},
            {}))
        my_sig = Signal({"key": "val"})
        blk.notify_management_signal(my_sig)
        service_mgmt_signal_handler.assert_called_once_with(my_sig)

    def test_notify_signals(self):
        """Test the block can notify signals properly"""
        blk = Block()
        my_sigs = [Signal({"key": "val"})]
        with patch.object(blk, '_block_router') as router_patch:
            blk.notify_signals(my_sigs)
            router_patch.notify_signals.assert_called_once_with(
                blk, my_sigs, DEFAULT_TERMINAL)

        # test sending more than one Signal
        with patch.object(blk, '_block_router') as router_patch:
            signals = [Signal(), Signal()]
            blk.notify_signals(signals, "default")
            router_patch.notify_signals.assert_called_one_with(
                blk, signals, "default")

        # test that sending signals as a set is allowed
        with patch.object(blk, '_block_router') as router_patch:
            signals = set()
            signals.add(Signal())
            signals.add(Signal())
            blk.notify_signals(signals, "default")
            router_patch.notify_signals.assert_called_one_with(
                blk, signals, "default")

        # test that a Signal as a non-iterable is accepted and
        # propagated as a list
        with patch.object(blk, '_block_router') as router_patch:
            single_signal = Signal()
            blk.notify_signals(single_signal, "default")
            router_patch.notify_signals.assert_called_one_with(
                blk, [single_signal], "default")

        # test that a dictionary, empty or not, is not accepted and
        # TypeError is raised
        dict_signal = {}
        with self.assertRaises(TypeError):
            blk.notify_signals(dict_signal, "default")

        dict_signal = {"key": "val"}
        with self.assertRaises(TypeError):
            blk.notify_signals(dict_signal, "default")

    def test_import_locations(self):
        """Make sure the block can be imported from the nio root"""
        from nio import Block as nioBlock
        self.assertEqual(nioBlock, Block)

    def test_block_properties(self):
        """Make sure the block's properties contains common properties"""
        blk = Block()
        props = blk.properties()
        self.assertIn('type', props)
        self.assertIn('log_level', props)
        self.assertIn('name', props)

    def test_block_description(self):
        """Make sure the block's description contains common properties"""
        desc = Block.get_description()
        self.assertIn('type', desc['properties'])
        self.assertIn('log_level', desc['properties'])
        self.assertIn('name', desc['properties'])
        self.assertIn('properties', desc['commands'])

    def test_default_block_terminals(self):
        """Make sure the block has its default terminals"""
        blk = Block()
        self.assertTrue(blk.is_input_valid(DEFAULT_TERMINAL))
        self.assertTrue(blk.is_output_valid(DEFAULT_TERMINAL))
        self.assertFalse(blk.is_input_valid('fake input'))
        self.assertFalse(blk.is_output_valid('fake output'))
