import logging

from nio.modules.communication.subscriber import Subscriber
from nio.util.logging.handlers.publisher.cache_filter import CacheFilter
from nio.util.logging.handlers.publisher.handler import PublisherHandler
from nio.util.logging.filter import NIOFilter

from nio.testing.test_case import NIOTestCase


class TestPublisherBase(NIOTestCase):

    def get_test_modules(self):
        return super().get_test_modules() | {'communication'}

    def add_cache_filter(self):
        """ Allows inheriting tests to decide on the use of the CacheFilter """
        return True

    def setUp(self):
        self._received_messages = []
        # Set up our publisher logger with the proper filters and handlers
        self._publisher_logger = logging.getLogger("service_name")

        publisher_topics = {"type": "logging"}
        self._handler = PublisherHandler(topics=publisher_topics)

        self._handler.setLevel(logging.INFO)
        self._handler.addFilter(NIOFilter())
        if self.add_cache_filter():
            self._handler.addFilter(
                CacheFilter(expire_interval=self.get_cache_interval()))
        self._publisher_logger.addHandler(self._handler)

        # Want to create our PublisherHandler before we call super setup,
        # the handler will initialize the PublisherProxy which should be
        # done before the modules are ready
        super().setUp()

        # Set up a test-wide handler for messages delivered through the
        # publisher
        self._subscriber = Subscriber(self._on_logger_signal,
                                      **publisher_topics)
        self._subscriber.open()

    def tearDown(self):
        self._publisher_logger.removeHandler(self._handler)
        self._handler.close()
        self._received_messages = []
        super().tearDown()

    def get_cache_interval(self):
        return 1

    def _on_logger_signal(self, signals):
        for signal in signals:
            self._received_messages.append(signal.message)


class TestPublisher(TestPublisherBase):

    def test_log_to_publisher(self):
        """ Asserts that logged messages at different levels are handled """
        debug_messages = ["debug message1", "debug message2"]
        warning_messages = ["warning message1", "warning message2"]
        error_messages = ["error message1", "error message2"]
        for message in warning_messages:
            self._publisher_logger.warning(message)
        for message in error_messages:
            self._publisher_logger.error(message)
        for message in debug_messages:
            self._publisher_logger.debug(message)

        for message in warning_messages:
            self.assertIn(message, self._received_messages)
        for message in error_messages:
            self.assertIn(message, self._received_messages)
        for message in debug_messages:
            self.assertNotIn(message, self._received_messages)
