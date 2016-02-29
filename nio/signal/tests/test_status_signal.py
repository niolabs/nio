from nio.util.runner import RunnerStatus
from nio.signal.status import ServiceStatusSignal, BlockStatusSignal
from nio.util.support.test_case import NIOTestCase


class TestStatusSignal(NIOTestCase):

    def test_service_status_signal(self):
        """ Ensure we can create a status signal for a service """
        signal = ServiceStatusSignal(
            RunnerStatus.warning,
            message="just testing",
            service_name="MyService")
        self.assertEqual(signal.service_name, "MyService")

    def test_block_status_signal(self):
        """ Ensure we can create a status signal for a block """
        signal = BlockStatusSignal(
            RunnerStatus.warning,
            message="just testing",
            block_name="MyBlock",
            service_name="MyService")
        self.assertEqual(signal.block_name, "MyBlock")
        self.assertEqual(signal.service_name, "MyService")
