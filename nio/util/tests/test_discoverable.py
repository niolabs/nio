from nio.testing.test_case import NIOTestCaseNoModules
from nio.util.discovery import discoverable, is_class_discoverable
from nio.block.base import Block


@discoverable
class DiscoverableBlock(Block):
    pass


class NonDiscoverableSubBlock(DiscoverableBlock):
    pass


@discoverable
class DiscoverableSubBlock(NonDiscoverableSubBlock):
    pass


class TestDiscoverable(NIOTestCaseNoModules):

    def test_subclass(self):
        """Tests that subclasses are not discoverable"""
        self.assertTrue(is_class_discoverable(DiscoverableBlock))
        self.assertFalse(is_class_discoverable(NonDiscoverableSubBlock))
        self.assertTrue(is_class_discoverable(DiscoverableSubBlock))
