from unittest.mock import Mock, patch

from nio import Block
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
        with patch('nio.service.base.Persistence') as persist:
            service.configure(ServiceContext(
                {"name": "ServiceName", "log_level": "WARNING"},
                block_router_type=BlockRouter
            ))
            # Make sure our persistence would have been configured with our
            # service name
            persist.configure.assert_called_once_with('ServiceName')
        # Make sure the name property got set properly
        self.assertEqual(service.name(), "ServiceName")
        self.assertIsNotNone(service.logger)

    def test_start_stop(self):
        """Makes sure service and blocks update statuses accordingly """
        service = Service()

        class Block1(Block):
            pass

        class Block2(Block):
            pass

        blocks = [{"type": Block1,
                   "properties": {'name': 'block1'}},
                  {"type": Block2,
                   "properties": {'name': 'block2'}}]

        service.do_configure(ServiceContext(
            {"name": "ServiceName", "log_level": "WARNING"},
            blocks=blocks,
            block_router_type=BlockRouter
        ))
        # verify that statuses were updated
        status = service.full_status()
        self.assertIn("service", status)
        self.assertEqual(status["service"], "configured")
        self.assertIn("block1", status)
        self.assertEqual(status["block1"], "configured")
        self.assertIn("block2", status)
        self.assertEqual(status["block2"], "configured")

        service.do_start()

        # verify that statuses were updated
        status = service.full_status()
        self.assertIn("service", status)
        self.assertEqual(status["service"], "started")
        self.assertIn("block1", status)
        self.assertEqual(status["block1"], "started")
        self.assertIn("block2", status)
        self.assertEqual(status["block2"], "started")

        self.assertEqual(len(service.blocks), 2)

        service.do_stop()

        # verify that statuses were updated
        status = service.full_status()
        self.assertIn("service", status)
        self.assertEqual(status["service"], "stopped")
        self.assertIn("block1", status)
        self.assertEqual(status["block1"], "stopped")
        self.assertIn("block2", status)
        self.assertEqual(status["block2"], "stopped")

    def test_commands(self):
        """ Asserts commands functionality """
        service = Service()

        service.do_configure(ServiceContext(
            {"name": "ServiceName", "log_level": "WARNING"},
            block_router_type=BlockRouter
        ))

        service.do_start()

        # check get_description and assert that info matches expectations
        description = service.get_description()
        self.assertIn("properties", description)
        self.assertIn("name", description["properties"])
        self.assertIn("auto_start", description["properties"])

        self.assertIn("commands", description)
        self.assertIn("start", description["commands"])
        self.assertIn("stop", description["commands"])
        self.assertIn("status", description["commands"])
        self.assertIn("heartbeat", description["commands"])
        self.assertIn("runproperties", description["commands"])

        # verify heartbeat command
        self.assertEqual(service.heartbeat().name, "started")

        # verify runproperties command
        run_properties = service.runproperties()
        self.assertIn("name", run_properties)
        self.assertEqual(run_properties["name"], "ServiceName")

        service.do_stop()

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
