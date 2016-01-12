from nio.util.support.test_case import NIOTestCase
from nio.common.discovery import DiscoverableType, Discoverable, \
    class_has_discoverable_type
from nio.block.base import Block


@Discoverable(DiscoverableType.block)
class DiscoverableBlock(Block):
    pass


class DiscoverableSubBlock(DiscoverableBlock):
    pass


class TestTypesManager(NIOTestCase):

    def test_subclass(self):
        """Tests that subclasses are not discoverable"""
        self.assertTrue(class_has_discoverable_type(
            DiscoverableBlock, DiscoverableType.block))

        self.assertFalse(class_has_discoverable_type(
            DiscoverableSubBlock, DiscoverableType.block))

    def test_discoverable_type(self):
        """Tests that the discoverable type is checked properly"""
        self.assertTrue(class_has_discoverable_type(
            DiscoverableBlock, DiscoverableType.block))

        self.assertFalse(class_has_discoverable_type(
            DiscoverableBlock, DiscoverableType.service))
