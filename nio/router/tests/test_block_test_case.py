from nio.router.base import InvalidBlockOutput
from nio.util.support.block_test_case import NIOBlockTestCase
from nio.block.base import Block
from nio.common.signal.base import Signal
from nio.common.signal.status import BlockStatusSignal
from nio.common import RunnerStatus


class TestBlockTestCase(NIOBlockTestCase):

    """ Tests that the BlockTestCase handles roter methods properly. """

    def signals_notified(self, signals, output_id='default'):
        """ Override a signal notification handler """
        self._signals_notified = True

    def management_signal_notified(self, signal):
        """ Override a management signal notification handler """
        self._management_notified = True

    def test_allows_signal_notify(self):
        """ Makes sure a test can assert how many signals were notified """
        b1 = Block()
        b2 = Block()
        self.configure_block(b1, {})
        self.configure_block(b2, {})

        b1.notify_signals([Signal(), Signal()])
        b2.notify_signals([Signal()])

        # Assert that 3 total signals were captured
        self.assert_num_signals_notified(3)

        # Assert that we captured the right number of signals per block too
        self.assert_num_signals_notified(2, b1)
        self.assert_num_signals_notified(1, b2)

    def test_allows_mgmt_signal_notify(self):
        """ Makes sure a test can assert how many mgmt sigs were notified """
        b1 = Block()
        b2 = Block()
        self.configure_block(b1, {})
        self.configure_block(b2, {})

        # First make sure our blocks have no status
        self.assert_block_status(b1, '')
        self.assert_block_status(b2, '')

        b1.notify_management_signal(BlockStatusSignal(RunnerStatus.error))
        self.assert_block_status(b1, RunnerStatus.error)
        self.assert_num_mgmt_signals_notified(1, b1)
        self.assert_num_mgmt_signals_notified(0, b2)

        b2.notify_management_signal(BlockStatusSignal(RunnerStatus.warning))
        self.assert_block_status(b2, RunnerStatus.warning)
        self.assert_num_mgmt_signals_notified(1, b1)
        self.assert_num_mgmt_signals_notified(1, b2)

        # Assert that 2 total signals were captured
        self.assert_num_mgmt_signals_notified(2)

    def test_allows_mgmt_signal_handler_override(self):
        """ Makes sure a test can override a management signal handler """
        self._management_notified = False
        b1 = Block()
        self.configure_block(b1, {})

        self.assertFalse(self._management_notified)
        b1.notify_management_signal(BlockStatusSignal(RunnerStatus.error))
        self.assertTrue(self._management_notified)

    def test_allows_signal_handler_override(self):
        """ Makes sure a test can override a signal handler """
        self._signals_notified = False
        b1 = Block()
        self.configure_block(b1, {})

        self.assertFalse(self._signals_notified)
        b1.notify_signals([Signal()])
        self.assertTrue(self._signals_notified)

    def test_invalid_output(self):
        """ Asserts that an an exception is raised when output is invalid """
        b1 = Block()
        self.configure_block(b1, {})

        with self.assertRaises(InvalidBlockOutput):
            b1.notify_signals([Signal()], "invalid_output")
