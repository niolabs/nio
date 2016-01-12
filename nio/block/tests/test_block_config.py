from nio.block.context import BlockContext
from nio.block.base import Block
from nio.common.block.router import BlockRouter
from nio.metadata.properties.string import StringProperty
from nio.util.support.test_case import NIOTestCase

CONFIG_KEY = "attr_1"
CONFIG_VAL = "attr_1_val"


class DummyBlock(Block):
    # Create a dummy block with my configurable attribute
    attr_1 = StringProperty()


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
        self._config = {"name":"dummy_block"}
        self._config[CONFIG_KEY] = CONFIG_VAL

    def test_load_config(self):
        """Test that a configuration can get loaded into the block"""
        block = DummyBlock()
        block.configure(BlockContext(BlockRouter(),
                                     self._config,
                                     dict(),
                                     None))

        self.assertEqual(getattr(block, CONFIG_KEY), CONFIG_VAL)

    def test_no_load_config(self):
        """Test that with no configuration the attribute exists,
            but is not set.
        """
        block = DummyBlock()
        block.configure(BlockContext(BlockRouter(),
                                     dict(),
                                     dict(),
                                     None))

        self.assertTrue(hasattr(block, CONFIG_KEY))
        self.assertNotEqual(getattr(block, CONFIG_KEY), CONFIG_VAL)
