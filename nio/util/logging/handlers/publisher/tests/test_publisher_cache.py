from .test_publisher import TestPublisherBase


class TestPublisherCache(TestPublisherBase):

    def get_cache_interval(self):
        return 1

    def test_log_to_publisher_cache(self):
        msg1 = "warning message1 cached"
        msg2 = "warning message2 cached"
        warning_messages = [msg1, msg1, msg1, msg2]
        for message in warning_messages:
            self._publisher_logger.warning(message)

        self.assertIn(msg1, self._received_messages)
        self.assertIn(msg2, self._received_messages)
        self._received_messages.remove(msg1)
        self._received_messages.remove(msg2)
        # proof that msg1 was received only once
        self.assertNotIn(msg1, self._received_messages)
        self.assertNotIn(msg2, self._received_messages)

        self._received_messages = []
        warning_messages = [msg1, msg2, msg1, msg2]
        # it will filter nothing, no consecutive messages with same text
        for message in warning_messages:
            self._publisher_logger.warning(message)

        for message in warning_messages:
            self.assertIn(message, self._received_messages)
            # proof that no message was filtered
            self._received_messages.remove(message)
        self.assertNotIn(msg1, self._received_messages)
        self.assertNotIn(msg2, self._received_messages)
