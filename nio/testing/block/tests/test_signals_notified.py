from nio.block.base import Block
from nio.block.terminals import output
from nio.signal.base import Signal
from nio.testing.block import NIOBlockTestCase


class TestDefaultTerminal(NIOBlockTestCase):

    @property
    def block_type(self):
        return Block

    def test_signals_default_terminal(self):
        """ Tests signals_notified when Block defines no output
        """
        self.configure_block({})

        # notify signals on default output
        default_output_signal1 = Signal({"name": "default_s1"})
        default_output_signal2 = Signal({"name": "default_s2"})
        # don't specify any output
        self.notify_signals([default_output_signal1, default_output_signal2])
        # grab signals notified
        signals_notified = self.signals_notified()
        self.assertIn(default_output_signal1, signals_notified)
        self.assertIn(default_output_signal2, signals_notified)

        # notify signals on named outputs
        attempt_named_output = Signal({"name": "o1_s1"})
        with self.assertRaises(ValueError):
            self.notify_signals([attempt_named_output], "output1")


@output("output1")
@output("output2")
class BlockWithOutputs(Block):
    pass


class TestBlockWithOutputs(NIOBlockTestCase):

    @property
    def block_type(self):
        return BlockWithOutputs

    def test_signals_notified(self):
        """ Tests signals_notified on a Block with outputs but no default
        """
        self.configure_block({})

        # notify signals on named outputs
        attempt_default_signal = Signal({"name": "d1_s1"})
        with self.assertRaises(ValueError):
            self.notify_signals([attempt_default_signal])

        # notify signals on named outputs
        output1_signal1 = Signal({"name": "o1_s1"})
        output1_signal2 = Signal({"name": "o1_s2"})
        self.notify_signals([output1_signal1, output1_signal2], "output1")

        # assert signals notified
        self.assertIn(output1_signal1, self.signals_notified())
        self.assertIn(output1_signal2, self.signals_notified())

        output2_signal1 = Signal({"name": "o2_s1"})
        output2_signal2 = Signal({"name": "o2_s2"})
        self.notify_signals([output2_signal1, output2_signal2], "output2")

        # assert output1 signals are not the signals notified by default anymore
        self.assertNotIn(output1_signal1, self.signals_notified())
        self.assertNotIn(output1_signal2, self.signals_notified())

        # assert now that signals notified on 'output2' are the
        # signals notified by default
        self.assertIn(output2_signal1, self.signals_notified())
        self.assertIn(output2_signal2, self.signals_notified())

        # assert notified signals for specified outputs
        self.assertIn(output1_signal1, self.signals_notified("output1"))
        self.assertIn(output1_signal2, self.signals_notified("output1"))
        self.assertIn(output2_signal1, self.signals_notified("output2"))
        self.assertIn(output2_signal2, self.signals_notified("output2"))

        # assert that when output is specified, it must be valid when getting
        # last signal from it
        with self.assertRaises(ValueError):
            self.assertEqual(self.signals_notified("INVALID_OUTPUT"),
                             None)


@output("output1", default=True)
@output("output2")
class BlockWithDefaultOutputSpecified(Block):
    pass


class TestBlockWithDefaultOutputSpecified(NIOBlockTestCase):

    @property
    def block_type(self):
        return BlockWithDefaultOutputSpecified

    def test_signals_notified_with_default_specified(self):
        """ Assert signals_notified when there is a default explicit input
        """
        self.configure_block({})

        # notify signals on default input
        default_output_signal1 = Signal({"name": "default_s1"})
        default_output_signal2 = Signal({"name": "default_s2"})
        self.notify_signals([default_output_signal1, default_output_signal2])

        # assert signals_notified without naming an output and signals_notified
        # when naming the default output yields the same result
        self.assertIn(default_output_signal1, self.signals_notified())
        self.assertIn(default_output_signal2, self.signals_notified())
        self.assertIn(default_output_signal1, self.signals_notified("output1"))
        self.assertIn(default_output_signal2, self.signals_notified("output1"))

        # notify signals on named output
        output1_signal1 = Signal({"name": "o1_s1"})
        output1_signal2 = Signal({"name": "o1_s2"})
        self.notify_signals([output1_signal1, output1_signal2], "output1")

        output2_signal1 = Signal({"name": "o2_s1"})
        output2_signal2 = Signal({"name": "o2_s2"})
        self.notify_signals([output2_signal1, output2_signal2], "output2")

        # assert signals were processes on expected outputs
        self.assertIn(output1_signal1, self.signals_notified("output1"))
        self.assertIn(output1_signal2, self.signals_notified("output1"))

        self.assertIn(output2_signal1, self.signals_notified("output2"))
        self.assertIn(output2_signal2, self.signals_notified("output2"))


class TestSignalRetrieval(NIOBlockTestCase):

    @property
    def block_type(self):
        return Block

    def test_multiple_notifications(self):
        """ Tests multiple signal notifications and how they are retrieved
        """
        self.configure_block({})

        # notify first list of signals
        signal11 = Signal({"name": "11"})
        signal12 = Signal({"name": "12"})
        signals1 = [signal11, signal12]
        self.notify_signals(signals1)

        # notify second list of signals
        signal21 = Signal({"name": "21"})
        signal22 = Signal({"name": "22"})
        signals2 = [signal21, signal22]
        self.notify_signals(signals2)

        # notify third list of signals
        signal31 = Signal({"name": "31"})
        signal32 = Signal({"name": "32"})
        signals3 = [signal31, signal32]
        self.notify_signals(signals3)

        # combined all signals into one list
        signals_notified = self.signals_notified()
        self.assertIn(signal11, signals_notified)
        self.assertIn(signal12, signals_notified)
        self.assertNotIn(signals1, signals_notified)
        self.assertIn(signal21, signals_notified)
        self.assertIn(signal22, signals_notified)
        self.assertNotIn(signals2, signals_notified)
        self.assertIn(signal31, signals_notified)
        self.assertIn(signal32, signals_notified)
        self.assertNotIn(signals3, signals_notified)
        self.assertEqual(len(signals_notified),
                         len(signals1) + len(signals2) + len(signals3))
        # assert order
        self.assertEqual(signal11, signals_notified[0])
        self.assertEqual(signal12, signals_notified[1])
        self.assertEqual(signal21, signals_notified[2])
        self.assertEqual(signal22, signals_notified[3])
        self.assertEqual(signal31, signals_notified[4])
        self.assertEqual(signal32, signals_notified[5])

        # obtain signals as notified
        signals_notified = self.signals_notified(combine_lists=False)
        self.assertNotIn(signal11, signals_notified)
        self.assertNotIn(signal12, signals_notified)
        self.assertIn(signals1, signals_notified)
        self.assertNotIn(signal21, signals_notified)
        self.assertNotIn(signal22, signals_notified)
        self.assertIn(signals2, signals_notified)
        self.assertNotIn(signal31, signals_notified)
        self.assertNotIn(signal32, signals_notified)
        self.assertIn(signals3, signals_notified)
        self.assertEqual(len(signals_notified), 3)
        # assert order
        self.assertEqual(signals1, signals_notified[0])
        self.assertEqual(signals2, signals_notified[1])
        self.assertEqual(signals3, signals_notified[2])