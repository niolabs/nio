from nio.common import RunnerStatus
from nio.common.signal.status import ServiceStatusSignal, \
    BlockStatusSignal, StatusSignal
from nio.util.support.test_case import NIOTestCase


class TestStatusSignal(NIOTestCase):
    """ These tests assert that StatusSignal's source field is set accordingly
    """

    def test_service_status_signal(self):
        signal = ServiceStatusSignal(RunnerStatus.warning, "from unit test")
        self.assertEqual(signal.source, "service")

    def test_block_status_signal(self):
        signal = BlockStatusSignal(RunnerStatus.warning, "from unit test")
        self.assertEqual(signal.source, "block")

    def test_unknown_source_status_signal(self):
        signal = StatusSignal(RunnerStatus.warning, "from unit test")
        self.assertEqual(signal.source, "unknown")
