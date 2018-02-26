from nio.block.base import Block
from nio.block.context import BlockContext
from nio.properties import StringProperty
from nio.router.base import BlockRouter
from nio.testing.test_case import NIOTestCase

CONFIG_KEY = "attr_1"
CONFIG_VAL = "attr_1_val"


class DummyBlock(Block):
    # Create a dummy block with my configurable attribute
    attr_1 = StringProperty(title="attr_1", allow_none=True)
    name = StringProperty(title="name", allow_none=True)


class TestBlockConfig(NIOTestCase):

    def setupModules(self):
        # Not using functionality modules
        pass

    def tearDownModules(self):
        # Not using functionality modules
        pass

    def setUp(self):
        # Build some sample configuration (don't actually load anything)
        super().setUp()
        self._config = {"id": "dummy_block", CONFIG_KEY: CONFIG_VAL}

    def test_load_config(self):
        """Test that a configuration can get loaded into the block"""
        block = DummyBlock()
        block.configure(BlockContext(BlockRouter(),
                                     self._config))

        self.assertEqual(getattr(block, CONFIG_KEY)(), CONFIG_VAL)

    def test_no_load_config(self):
        """Test that with no configuration the attribute exists, but not set"""
        block = DummyBlock()
        block.configure(BlockContext(BlockRouter(),
                                     {"id": "BlockId"}))

        self.assertTrue(hasattr(block, CONFIG_KEY))
        self.assertEqual(getattr(block, CONFIG_KEY)(), None)
        self.assertNotEqual(getattr(block, CONFIG_KEY)(), CONFIG_VAL)
