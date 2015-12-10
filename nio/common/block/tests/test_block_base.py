from nio.common.block.base import Block
from nio.common.block.context import BlockContext
from nio.util.support.test_case import NIOTestCase


class InvalidBlock(object):
    pass


class TestBaseBlock(NIOTestCase):

    def test_invalid_block_router(self):
        self.assertRaises(
            TypeError, Block().configure,
            BlockContext(InvalidBlock, {}, {}, None))

    def test_block_properties(self):
        blk = Block()
        props = blk.properties()
        self.assertIn('type', props)
        self.assertIn('log_level', props)
        self.assertIn('name', props)
