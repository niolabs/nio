from unittest.mock import MagicMock
from nio.block.mixins.group_by.group_by import GroupBy
from nio.block.base import Block, DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase


class GroupingBlock(GroupBy, Block):

    def __init__(self):
        super().__init__()
        self._data = {}
        self._group_count = 0

    def process_group_signals(self, signals, group, input_id=None):
        self._data[group] = signals
        return [Signal({"group": group})]

    def process_group_without_signals(self, group):
        self._group_count += 1


class NoOutputBlock(GroupBy, Block):

    def process_group_signals(self, signals, group, input_id=None):
        return []


class TestGroupBy(NIOBlockTestCase):

    def test_default(self):
        """ Test the default behavior of the group by notification """
        block = GroupingBlock()
        self.configure_block(block, {
            "group_by": "{{ $group }}"
        })
        # Notify 3 signals into the block
        block.process_signals([
            Signal({"group": 1, "value": 1}),
            Signal({"group": 2, "value": 1}),
            Signal({"group": 1, "value": 2})
        ])
        # Based on the block's implementation of process_group_signals,
        # two signals should be notified, one for each group
        self.assert_num_signals_notified(2)

    def test_signals_returned(self):
        """ Tests we can return signals and have them notified """
        block = GroupingBlock()
        self.configure_block(block, {
            "group_by": "{{ $group }}"
        })
        block.process_signals([
            Signal({"group": 1, "value": 1}),
            Signal({"group": 1, "value": 2})
        ])
        self.assert_num_signals_notified(1)

        # last_notified alias should work here as well
        self.assertEqual(self.last_notified[DEFAULT_TERMINAL][0].group,
                         1)
        self.assertEqual(self.notified_signals[DEFAULT_TERMINAL][0][0].group,
                         1)

    def test_for_each(self):
        """Test we can call for_each_group in our own block"""
        block = GroupingBlock()
        self.configure_block(block, {
            "group_by": "{{ $group }}"
        })
        signals = [
            Signal({"group": "1"}),
            Signal({"group": "2"}),
            Signal({"group": "3"}),
            Signal({"group": "1"})
        ]
        block.for_each_group(block.process_group_signals, signals)
        block.for_each_group(block.process_group_without_signals)
        # Should have 3 records in our block data, one for each group
        self.assertEqual(len(block._data), 3)
        self.assertSetEqual(set(block._data.keys()), {"1", "2", "3"})
        # Group 1 should have 2 signals
        self.assertEqual(len(block._data["1"]), 2)
        self.assertEqual(block._group_count, 3)

    def test_expr_fail(self):
        """ Test group_by expression fails raise exceptions """
        block = GroupingBlock()
        self.configure_block(block, {
            "group_by": "{{$foo + 1}}"
        })
        signals = [
            Signal({"foo": 1}),
            Signal({"foo": "wozzle"}),
            Signal({"foo": "bar"}),
            Signal({"foo": 5})
        ]
        # Signals with errors in group by should be ignored
        with self.assertRaises(TypeError):
            block.for_each_group(block.process_group_signals, signals)
        # A group should have been created for the first signal, but
        # not made it to the last
        self.assertEqual(len(block._groups), 1)
        self.assertEqual(block._groups, {1 + 1})

    def test_unhashable(self):
        """ Test what happens when unhashable types are the groups """
        block = GroupingBlock()
        self.configure_block(block, {
            "group_by": "{{$foo}}"
        })
        signals = [
            Signal({"foo": [1]}),
            Signal({"foo": [2]}),
            Signal({"foo": {3: 4}})
        ]
        block.for_each_group(block.process_group_signals, signals)
        block.for_each_group(block.process_group_without_signals)

        # Since lists and dicts are not hashable, they will defer to their
        # string representations for the group key
        self.assertEqual(len(block._data["[1]"]), 1)
        self.assertEqual(block._group_count, 3)

    def test_for_each_return_list(self):
        """ Test that for each group returns the extended list of returns """
        block = GroupingBlock()
        self.configure_block(block, {
            "group_by": "{{$foo}}"
        })
        signals = [
            Signal({"foo": "wozzle", "val": 1}),
            Signal({"foo": "bar", "val": 2}),
            Signal({"foo": "pity", "val": 3}),
            Signal({"foo": "bar", "val": 4})
        ]

        def target_func(signals, group_key):
            """ Returns list of all values in signals """
            return [s.val for s in signals]

        out = block.for_each_group(target_func, signals)
        self.assertEqual(sorted(out), [1, 2, 3, 4])

    def test_for_each_return_non_list(self):
        """ Test that for each group can return a non-list of return values """
        block = GroupingBlock()
        self.configure_block(block, {
            "group_by": "{{$foo}}"
        })
        signals = [
            Signal({"foo": "wozzle", "val": 1}),
            Signal({"foo": "bar", "val": 2}),
            Signal({"foo": "pity", "val": 3}),
            Signal({"foo": "bar", "val": 4})
        ]

        def target_func(signals, group_key):
            """ Return the actual sum this time, not a list """
            return sum([s.val for s in signals])

        out = block.for_each_group(target_func, signals)
        self.assertEqual(sorted(out), [1, 3, 6])

    def test_for_each_without_signals_return_list(self):
        """ Test that for each w/o signals returns the extended list """
        block = GroupingBlock()
        self.configure_block(block, {
            "group_by": "{{$foo}}"
        })
        # Simulate some fake groups being added
        block._groups = {"bar", "foo"}

        def target_func(group_key):
            # Return a single item, wrapped in a list
            return [group_key]

        out = block.for_each_group(target_func)
        self.assertEqual(sorted(out), ["bar", "foo"])

    def test_for_each_without_signals_return_non_list(self):
        """ Test that for each w/o signals can return individual items """
        block = GroupingBlock()
        self.configure_block(block, {
            "group_by": "{{$foo}}"
        })
        # Simulate some fake groups being added
        block._groups = {"bar", "foo"}

        def target_func(group_key):
            # Return a single item, no list
            return group_key

        out = block.for_each_group(target_func)
        self.assertEqual(sorted(out), ["bar", "foo"])

    def test_require_process_group_signals_implementation(self):
        """ Make sure that a block implements process_group_signals """

        class NoProcessGroupBlock(GroupBy, Block):
            pass

        block = NoProcessGroupBlock()
        self.configure_block(block, {})
        block.start()
        # Block didn't implement process_group_signals but wants to use the
        # default implementation of process_signals. This is not allowed
        with self.assertRaises(NotImplementedError):
            block.process_signals([Signal])
        block.stop()

    def test_groups(self):
        """ Test that 'groups' command return groups as they are added """
        block = GroupingBlock()
        self.configure_block(block, {
            "group_by": "{{ $group }}"
        })

        block_groups = block._groups_command()
        self.assertDictEqual(block_groups, {"groups": []})

        # Notify 3 signals into the block
        block.process_signals([
            Signal({"group": 1, "value": 1}),
            Signal({"group": 2, "value": 1}),
            Signal({"group": 1, "value": 2})
        ])

        # verify created groups
        expected_groups = {"groups": [1, 2]}
        block_groups = block._groups_command()
        self.assertDictEqual(expected_groups, block_groups)

        block.process_signals([
            Signal({"group": 3, "value": 3})
        ])

        expected_groups = {"groups": [1, 2, 3]}
        block_groups = block._groups_command()
        self.assertDictEqual(expected_groups, block_groups)

    def test_no_output(self):
        """If process_group_signals returns empty lists, don't notify them"""
        block = NoOutputBlock()
        self.configure_block(block, {})
        block.notify_signals = MagicMock()
        block.process_signals([
            Signal({"group": 1, "value": 1}),
            Signal({"group": 2, "value": 1}),
            Signal({"group": 1, "value": 2})
        ])
        self.assertFalse(block.notify_signals.called)
