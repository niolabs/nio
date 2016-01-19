from unittest.mock import patch
from nio.block.base import Block
from nio.block.context import BlockContext
from nio.common.signal.base import Signal
from nio.router.base import BlockRouter
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
        self.assertEqual(blk.name, "BlockName")

    def test_invalid_configure(self):
        """Make sure a block is configured with valid information"""
        class JustAnObject(object):
            pass
        with self.assertRaises(TypeError):
            # Can't configure with a non BlockContext
            Block().configure(JustAnObject)
        with self.assertRaises(TypeError):
            # The context's block router needs to be a BlockRouter
            Block().configure(BlockContext(JustAnObject, {}, {}, None))

    def test_notify_management_signal(self):
        """Test the block can notify management signals properly"""
        blk = Block()
        my_sig = Signal({"key": "val"})
        with patch.object(blk, '_block_router') as router_patch:
            blk.notify_management_signal(my_sig)
            router_patch.notify_management_signal.assert_called_once_with(
                blk, my_sig)

    def test_notify_signals(self):
        """Test the block can notify signals properly"""
        # TODO: Once NIO-768 is done, this test should be greatly expanded
        blk = Block()
        my_sigs = [Signal({"key": "val"})]
        with patch.object(blk, '_block_router') as router_patch:
            blk.notify_signals(my_sigs, "default")
            router_patch.notify_signals.assert_called_once_with(
                blk, my_sigs, "default")

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
        self.assertTrue(blk.is_input_valid('default'))
        self.assertTrue(blk.is_output_valid('default'))
        self.assertFalse(blk.is_input_valid('fake input'))
        self.assertFalse(blk.is_output_valid('fake output'))
