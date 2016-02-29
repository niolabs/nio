from nio.block.mixins.collector.collector import Collector
from nio.block.base import Block
from nio.signal.base import Signal
from nio.util.support.block_test_case import NIOBlockTestCase
from time import sleep


class DummyBlock(Collector, Block):
    pass


class TestCollector(NIOBlockTestCase):

    def test_collects(self):
        """Test that the block collects the way it is supposed to.

        Run for 5 seconds, collecting every 2 seconds. Spit out a signal every
        second but make sure that only 4 got collected and notified
        """
        block = DummyBlock()
        self.configure_block(block, {
            "collect": {'seconds': 2}
        })
        block.start()

        for _ in range(5):
            block.notify_signals([Signal()])
            sleep(1.1)

        block.stop()
        self.assert_num_signals_notified(4)

    def test_no_collect_on_zero(self):
        """Test that the block does not collect if 0 timeout is specified"""
        block = DummyBlock()
        self.configure_block(block, {
            "collect": {'seconds': 0}
        })
        block.start()

        for _ in range(5):
            block.notify_signals([Signal()])

        block.stop()
        self.assert_num_signals_notified(5)
