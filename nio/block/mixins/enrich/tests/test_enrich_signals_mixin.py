from nio.block.mixins.enrich.enrich_signals import EnrichSignals
from nio.block.base import Block, DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.util.support.block_test_case import NIOBlockTestCase


class DummyBlock(EnrichSignals, Block):
    pass


class TestEnrichSignals(NIOBlockTestCase):

    def test_exclude_existing(self):
        """ Make sure we can just return new data """
        blk = DummyBlock()
        self.set_up_block(blk, True, 'doesnt matter')
        incoming_signal = Signal({
            'key1': 'val1',
            'key2': 'val2'
        })

        result_dict = {'a': 1, 'b': 2}
        out_sig = blk.get_output_signal(result_dict, incoming_signal)

        # Make sure the output signal only has the result data
        self.assertDictEqual(result_dict, out_sig.to_dict())

    def test_add_to_field(self):
        """ Make sure we can add results to a new field on the signal """
        blk = DummyBlock()
        self.set_up_block(blk, False, 'results')
        incoming_signal = Signal({
            'key1': 'val1',
            'key2': 'val2'
        })

        result_dict = {'a': 1, 'b': 2}
        out_sig = blk.get_output_signal(result_dict, incoming_signal)

        # Make sure our results got put on the results attribute
        self.assertDictEqual(result_dict, out_sig.results)
        # Make sure our original data is still there too
        self.assertEqual(out_sig.key1, 'val1')
        self.assertEqual(out_sig.key2, 'val2')

    def test_signal_merge(self):
        """ Make sure we can add results to a new field on the signal """
        blk = DummyBlock()
        self.set_up_block(blk, False, '')
        incoming_signal = Signal({
            'key1': 'val1',
            'key2': 'val2'
        })

        result_dict = {'a': 1, 'b': 2, 'key2': 'new val2'}
        out_sig = blk.get_output_signal(result_dict, incoming_signal)

        # Make sure our new data is on the signal
        self.assertEqual(out_sig.a, 1)
        self.assertEqual(out_sig.b, 2)
        # Make sure our original data is still there too
        self.assertEqual(out_sig.key1, 'val1')
        # But key2 should have the result's value rather than the original
        self.assertEqual(out_sig.key2, 'new val2')

    def test_copy(self):
        """ Make sure that incoming signals can be copied """
        blk = DummyBlock()
        self.set_up_block(blk, False, 'results')
        incoming_signal = Signal({
            'key1': 'val1',
            'key2': 'val2'
        })

        result_dict = {'a': 1, 'b': 2}
        out_sig = blk.get_output_signal(result_dict, incoming_signal,
                                        copy=True)

        incoming_signal.key1 = 'updated val1'

        # Only our output signal should have the results set
        self.assertTrue(hasattr(out_sig, 'results'))
        self.assertFalse(hasattr(incoming_signal, 'results'))

        # The updated value should not afect our output signal
        self.assertEqual(out_sig.key1, 'val1')
        self.assertEqual(incoming_signal.key1, 'updated val1')

    def test_no_copy(self):
        """ Make sure that incoming signals can be copied """
        blk = DummyBlock()
        self.set_up_block(blk, False, 'results')
        incoming_signal = Signal({
            'key1': 'val1',
            'key2': 'val2'
        })

        result_dict = {'a': 1, 'b': 2}
        out_sig = blk.get_output_signal(result_dict, incoming_signal,
                                        copy=False)

        incoming_signal.key1 = 'updated val1'

        # Both signals should have the results now
        self.assertTrue(hasattr(out_sig, 'results'))
        self.assertTrue(hasattr(incoming_signal, 'results'))

        # The updated value should also afect our output signal
        self.assertEqual(out_sig.key1, 'updated val1')
        self.assertEqual(incoming_signal.key1, 'updated val1')

    def test_notified(self):
        """ Make sure we notify the signals properly """
        blk = DummyBlock()
        self.set_up_block(blk, False, '')
        incoming_signal = Signal({
            'key1': 'val1',
            'key2': 'val2'
        })

        # Try sending 3 results and make sure 3 signals get notified
        results = [{'num': 1}, {'num': 2}, {'num': 3}]
        blk.notify_output_signals(results, incoming_signal, copy=True)
        self.assert_num_signals_notified(3)

        # Now send a single dictionary and make sure only one signal gets
        # notified
        blk.notify_output_signals({'num': 4}, incoming_signal, copy=True)
        self.assert_num_signals_notified(4)

        self.assertEqual(self.last_notified[DEFAULT_TERMINAL][0].num, 1)
        self.assertEqual(self.last_notified[DEFAULT_TERMINAL][1].num, 2)
        self.assertEqual(self.last_notified[DEFAULT_TERMINAL][2].num, 3)
        self.assertEqual(self.last_notified[DEFAULT_TERMINAL][3].num, 4)

    def set_up_block(self, block, exclude, field):
        self.configure_block(block, {
            'enrich': {
                'exclude_existing': exclude,
                'enrich_field': field
            }
        })
