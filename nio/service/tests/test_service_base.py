from unittest.mock import Mock

from nio.properties.exceptions import AllowNoneViolation
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

    def test_config_with_no_name(self):
        """Make sure a service cononfig has required 'name' property."""
        service = Service()
        with self.assertRaises(AllowNoneViolation):
            service.configure(ServiceContext({}))

    def test_invalid_config(self):
        """Make sure a service cononfig fails with invalid property config."""
        invalid_configs = [
            {"name": "ServiceName", "log_level": 42},
            {"name": "ServiceName", "execution": "not a list"},
            {"name": "ServiceName", "mappings": "not a list"},
        ]
        for config in invalid_configs:
            service = Service()
            with self.assertRaises(TypeError):
                service.configure(ServiceContext(config))

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
