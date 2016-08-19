from nio.block.base import Block
from nio.signal.base import Signal
from nio.testing.block import NIOBlockTestCase


class TestLastSignalsNotified(NIOBlockTestCase):

    @property
    def block_type(self):
        return Block

    def test_last_signals_notified(self):
        """ Tests last_signals_notified using multiple signal notifications
        """
        self.configure_block({})

        # notify first list of signals
        signal11 = Signal({"name": "11"})
        signal12 = Signal({"name": "12"})
        signals1 = [signal11, signal12]
        self.notify_signals(signals1)
        self.assertEqual(self.last_signals_notified(), signals1)

        # notify second list of signals
        signal21 = Signal({"name": "21"})
        signal22 = Signal({"name": "22"})
        signals2 = [signal21, signal22]
        self.notify_signals(signals2)
        # assert that signals2 are now the last signals notified
        self.assertEqual(self.last_signals_notified(), signals2)

        # notify third list of signals
        signal31 = Signal({"name": "31"})
        signal32 = Signal({"name": "32"})
        signals3 = [signal31, signal32]
        self.notify_signals(signals3)
        # assert that signals3 are now the last signals notified
        self.assertEqual(self.last_signals_notified(), signals3)
