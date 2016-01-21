import logging
from nio.modules.communication.subscriber import Subscriber
from nio.util.logging.handlers.publisher.handler import PublisherHandler
from nio.util.logging.filter import NIOFilter

from nio.util.support.test_case import NIOTestCase


class TestPublisherBase(NIOTestCase):

    def get_test_modules(self):
        return super().get_test_modules() | {'publisher', 'subscriber'}

    def setUp(self):
        self._received_messages = []
        # Set up our publisher logger with the proper filters and handlers
        self._publisher_logger = logging.getLogger("service_name")
        self._handler = PublisherHandler(
            cache_expire_interval=self.get_cache_interval())
        self._handler.setLevel(logging.INFO)
        self._handler.addFilter(NIOFilter())
        self._publisher_logger.addHandler(self._handler)

        # Want to create our PublisherHandler before we call super setup,
        # the handler will initialize the PublisherProxy which should be
        # done before the modules are ready
        super().setUp()

        # Set up a test-wide handler for messages delivered through the
        # publisher
        self._subscriber = Subscriber(self._on_logger_signal, type=["logging"])
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
