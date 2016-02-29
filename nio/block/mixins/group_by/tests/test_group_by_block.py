from nio.block.mixins.group_by.group_by import GroupBy
from nio.block.base import Block
from nio.signal.base import Signal
from nio.util.support.block_test_case import NIOBlockTestCase


class DummyBlock(GroupBy, Block):

    def __init__(self):
        super().__init__()
        self._data = {}
        self._group_count = 0

    def process_group(self, signals, key):
        self._data[key] = signals

    def inc_group(self, key):
        self._group_count += 1


class TestGroupBy(NIOBlockTestCase):

    def test_for_each(self):
        block = DummyBlock()
        self.configure_block(block, {
            "group_by": "{{$foo}}"
        })
        signals = [
            Signal({"foo": "wozzle"}),
            Signal({"foo": "bar"}),
            Signal({"foo": "pity"}),
            Signal({"foo": "bar"})
        ]
        block.for_each_group(block.process_group, signals)
        block.for_each_group(block.inc_group)
        self.assertCountEqual(block._data.keys(), ["wozzle", "bar", "pity"])
        self.assertEqual(len(block._data["bar"]), 2)
        self.assertEqual(block._group_count, 3)

    def test_del_group(self):
        block = DummyBlock()
        self.configure_block(block, {
            "group_by": "{{$foo}}"
        })
        signals = [
            Signal({"foo": "wozzle"}),
            Signal({"foo": "bar"}),
            Signal({"foo": "pity"}),
            Signal({"foo": "bar"})
        ]
        checked_groups = []

        def del_group(key):
            checked_groups.append(key)
            if key == 'wozzle':
                block._groups.remove(key)

        block.for_each_group(block.process_group, signals)
        self.assertEqual(['wozzle', 'bar', 'pity'], block._groups)
        block.for_each_group(del_group)
        self.assertEqual(['wozzle', 'bar', 'pity'], checked_groups)
        self.assertEqual(['bar', 'pity'], block._groups)

    def test_expr_fail(self):
        """ Test what happens when the group_by expression fails """
        block = DummyBlock()
        self.configure_block(block, {
            "group_by": "{{$foo + 1}}"
        })
        signals = [
            Signal({"foo": "wozzle"}),
            Signal({"foo": "bar"}),
            Signal({"foo": 1}),
            Signal({"foo": 5})
        ]
        # Signals with errors in group by should be ignored
        block.for_each_group(block.process_group, signals)
        block.for_each_group(block.inc_group)
        # We should only have groups for legit keys
        self.assertEqual(block._group_count, 2)
        self.assertEqual(len(block._data[6]), 1)

    def test_unhashable(self):
        """ Test what happens when unhashable types are the groups """
        block = DummyBlock()
        self.configure_block(block, {
            "group_by": "{{$foo}}"
        })
        signals = [
            Signal({"foo": [1]}),
            Signal({"foo": [2]}),
            Signal({"foo": {3: 4}})
        ]
        block.for_each_group(block.process_group, signals)
        block.for_each_group(block.inc_group)

        # Since lists and dicts are not hashable, they will defer to their
        # string representations for the group key
        self.assertEqual(len(block._data["[1]"]), 1)
        self.assertEqual(block._group_count, 3)

    def test_for_each_return(self):
        """ Test that for each group returns the list of return values """
        block = DummyBlock()
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
            """ Sum all values in signals """
            return sum([s.val for s in signals])

        out = block.for_each_group(target_func, signals)
        self.assertEqual(sorted(out), [1, 3, 6])

    def test_for_each_return_list(self):
        """ Test that for each group returns the extended list of returns """
        block = DummyBlock()
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
