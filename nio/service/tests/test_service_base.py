from unittest.mock import Mock

from nio.router.base import BlockRouter
from nio.service.base import Service
from nio.service.context import ServiceContext
from nio.signal.base import Signal
from nio.util.support.test_case import NIOTestCaseNoModules


class TestBaseService(NIOTestCaseNoModules):

    def test_configure(self):
        """Make sure a service can be configured"""
        service = Service()
        service.configure(ServiceContext(
            {"name": "ServiceName", "log_level": "WARNING"},
            block_router_type=BlockRouter
        ))
        # Make sure the name property got set properly
        self.assertEqual(service.name(), "ServiceName")

    def test_notify_management_signal(self):
        """Test the service can notify management signals properly"""
        service = Service()
        service_mgmt_signal_handler = Mock()
        service.configure(ServiceContext(
            {"name": "ServiceName", "log_level": "WARNING"},
            block_router_type=BlockRouter,
            mgmt_signal_handler=service_mgmt_signal_handler))
        my_sig = Signal({"key": "val"})
        service.mgmt_signal_handler(my_sig)
        service_mgmt_signal_handler.assert_called_once_with(my_sig)
