from unittest.mock import patch

from nio import Signal
from nio.testing.test_case import NIOTestCase
from nio.util.logging.handlers.publisher.proxy import PublisherProxy, \
    PublisherNotReadyException


class TestPublisherProxy(NIOTestCase):

    def get_test_modules(self):
        return super().get_test_modules() | {'communication'}

    def test_publisher_create_failure(self):
        """ Asserts that ready event is not set when Publisher cannot be created
        """
        topic = "logging"
        # set no waiting for publisher to be ready
        max_publisher_ready_time = 0
        publisher_ready_wait_interval_time = 0.01

        with patch('nio.util.logging.handlers.publisher.proxy.Publisher',
                   side_effect=NotImplementedError()):
            PublisherProxy.init(topic,
                                max_publisher_ready_time,
                                publisher_ready_wait_interval_time)

            self.assertFalse(PublisherProxy._publisher_ready_event.is_set())
            # assert that when a Publisher can't be created, the event
            # remains unset
            self.assertFalse(PublisherProxy._publisher_ready_event.wait(0.1))

            # assert than when trying to publish the exception is raised
            with self.assertRaises(PublisherNotReadyException):
                PublisherProxy.publish([Signal()])

        PublisherProxy.close()

    def test_publisher_create_ok(self):
        """ Asserts that signal is published when ready time is 1
        """
        topic = "logging"
        # set a maximum of 1 second for publisher to be ready
        max_publisher_ready_time = 1
        publisher_ready_wait_interval_time = 0.01

        PublisherProxy.init(topic,
                            max_publisher_ready_time,
                            publisher_ready_wait_interval_time)
        PublisherProxy.publish([Signal()])
        PublisherProxy.close()
