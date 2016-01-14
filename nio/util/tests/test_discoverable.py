from nio.util.support.test_case import NIOTestCaseNoModules
from nio.util.discovery import discoverable, _class_is_discoverable
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
        self.assertTrue(_class_is_discoverable(DiscoverableBlock))
        self.assertFalse(_class_is_discoverable(NonDiscoverableSubBlock))
        self.assertTrue(_class_is_discoverable(DiscoverableSubBlock))
