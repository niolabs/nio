from unittest.mock import patch
from datetime import timedelta
from nio.block.mixins.collector.collector import Collector
from nio.block.base import Block
from nio.signal.base import Signal
from nio.util.support.block_test_case import NIOBlockTestCase


class CollectingBlock(Collector, Block):
    pass


class TestCollector(NIOBlockTestCase):

    def test_collects(self):
        """Test that the block collects the way it is supposed to.

        Run for 5 seconds, collecting every 2 seconds. Spit out a signal every
        second but make sure that only 4 got collected and notified
        """
        block = CollectingBlock()
        self.configure_block(block, {
            "collect": {'seconds': 2}
        })
        with patch('nio.block.mixins.collector.collector.Job') as job_mock:
            block.start()
            # Make sure the repeatable job gets created and will run every 2s
            job_mock.assert_called_once_with(
                block._dump_signals, timedelta(seconds=2), True)

        # Notify 3 signals
        block.notify_signals([Signal()])
        block.notify_signals([Signal()])
        block.notify_signals([Signal()])
        # Simulate a job trigger by calling dump_signals
        block._dump_signals()
        # Notify 2 more signals
        block.notify_signals([Signal()])
        block.notify_signals([Signal()])
        # We should only have 3 signals notified so far since the second
        # dump hasn't occurred yet
        self.assert_num_signals_notified(3)
        # Simulate a job trigger by calling dump_signals again, then make sure
        # all 5 signals were notified
        block._dump_signals()
        self.assert_num_signals_notified(5)
        block.stop()

    def test_no_collect_on_zero(self):
        """Test that the block does not collect if 0 timeout is specified"""
        block = CollectingBlock()
        self.configure_block(block, {
            "collect": {'seconds': 0}
        })
        block.start()
        for _ in range(5):
            block.notify_signals([Signal()])
        block.stop()
        self.assert_num_signals_notified(5)

    def test_multiple_output_ids(self):
        """Make sure the block can keep track of different output IDs"""
        block = CollectingBlock()
        self.configure_block(block, {
            "collect": {'seconds': 2}
        })
        # Don't actually want to start a job, we'll simulate the job triggers
        with patch('nio.block.mixins.collector.collector.Job'):
            block.start()
        # Notify some signals, 2 on one output, 1 on another
        block.notify_signals([Signal()], 'output1')
        block.notify_signals([Signal()], 'output2')
        block.notify_signals([Signal()], 'output1')
        # No signals notified until the dump occurs
        self.assert_num_signals_notified(0)
        block._dump_signals()
        self.assert_num_signals_notified(2, block, 'output1')
        self.assert_num_signals_notified(1, block, 'output2')
        # A few more signals, but only on the first output
        block.notify_signals([Signal()], 'output1')
        block.notify_signals([Signal()], 'output1')
        block._dump_signals()
        self.assert_num_signals_notified(4, block, 'output1')
        # No more should have been notified on the second output
        self.assert_num_signals_notified(1, block, 'output2')
