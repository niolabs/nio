from nio.block.base import Block
from nio.common.block.controller import BlockController, BlockState,\
    BlockStatus
from nio.common.signal.management import ManagementSignal
from nio.util.support.test_case import NIOTestCase
from nio.block.context import BlockContext


class SampleBlock(Block):

    def __init__(self):
        super().__init__()
        self._configure_called = False
        self._start_called = False
        self._stop_called = False

    def start(self):
        super().start()
        self._start_called = True

    def configure(self, context):
        super().configure(context)
        self._configure_called = True

    def stop(self):
        super().stop()
        self._stop_called = True


# noinspection PyProtectedMember
class TestBlockController(NIOTestCase):

    def test_invalid_type(self):
        block_controller = BlockController(None)
        self.assertEqual(block_controller.state, BlockState.creating)

        # cannot create block type
        self.assertRaises(TypeError, block_controller.configure, None)

    def test_invalid_context(self):
        block_controller = BlockController(SampleBlock)
        self.assertEqual(block_controller.state, BlockState.creating)
        self.assertEqual(block_controller.status, BlockStatus.ok)

        # cannot access anything inside context
        self.assertRaises(AttributeError, block_controller.configure, None)

    def test_invalid_properties(self):
        context = BlockContext(None, None, None, None)
        block_controller = BlockController(SampleBlock)

        # properties to configure block are invalid
        self.assertRaises(TypeError, block_controller.configure, context)

    def test_controller_name(self):
        context = BlockContext(None,
                               {"name": "SampleBlock",
                                "log_level": "DEBUG"},
                               None, None)
        block_controller = BlockController(SampleBlock)

        block_controller.configure(context)

        self.assertEqual(block_controller.name, block_controller._block.name)
        block_controller.name = "FreeSample"
        self.assertEqual(block_controller.name, "FreeSample")
        self.assertEqual(block_controller.name, block_controller._block.name)

    def test_start_stop(self):
        """ Verifies normal execution.
        """
        context = BlockContext(None,
                               {"name": "SampleBlock",
                                "log_level": "DEBUG"},
                               None, None)
        block_controller = BlockController(SampleBlock)

        block_controller.configure(context)
        self.assertEqual(block_controller.state, BlockState.configured)
        self.assertTrue(block_controller._block._configure_called)

        self.assertFalse(block_controller._block._start_called)
        block_controller.start()
        self.assertEqual(block_controller.state, BlockState.started)

        self.assertTrue(block_controller._block._start_called)

        self.assertFalse(block_controller._block._stop_called)
        block_controller.stop()
        self.assertEqual(block_controller.state, BlockState.stopped)
        self.assertTrue(block_controller._block._stop_called)

    def test_management_signal(self):
        context = BlockContext(None,
                               {"name": "SampleBlock",
                                "log_level": "DEBUG"},
                               None, None,
                               mgmt_signal_handler=self._on_mgmt_signals)
        block_controller = BlockController(SampleBlock)

        block_controller.configure(context)
        self.assertEqual(block_controller.state, BlockState.configured)
        self.assertTrue(block_controller._block._configure_called)

        self.assertFalse(block_controller._block._start_called)
        block_controller.start()
        self.assertEqual(block_controller.state, BlockState.started)

        self.assertTrue(block_controller._block._start_called)

        self._received_mgmt_signal = None
        self._mgmt_signal = ManagementSignal(
            {"source": "test_management_signal"})
        block_controller.notify_management_signal(None,
                                                  self._mgmt_signal)
        self.assertEquals(self._mgmt_signal, self._received_mgmt_signal)

        self.assertFalse(block_controller._block._stop_called)
        block_controller.stop()
        self.assertEqual(block_controller.state, BlockState.stopped)
        self.assertTrue(block_controller._block._stop_called)

    def _on_mgmt_signals(self, signals):
        self._received_mgmt_signal = signals[0]
