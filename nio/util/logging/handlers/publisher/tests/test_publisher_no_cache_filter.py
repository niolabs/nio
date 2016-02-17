from nio.util.logging.handlers.publisher.tests.test_publisher \
    import TestPublisherBase


class TestPublisherNoCacheFilter(TestPublisherBase):

    def add_cache_filter(self):
        return False

    def test_log_to_publisher_no_cache_filter(self):
        """ Asserts that when cache filter is not added, no caching takes place
        """
        msg1 = "warning message1 nocache"
        msg2 = "warning message2 nocache"
        warning_messages = [msg1, msg1, msg1, msg2]

        for message in warning_messages:
            self._publisher_logger.warning(message)

        self.assertIn(msg1, self._received_messages)
        self.assertIn(msg2, self._received_messages)
        self._received_messages.remove(msg1)
        self._received_messages.remove(msg2)
        # proof that msg1 was received the second time
        self.assertIn(msg1, self._received_messages)
        self._received_messages.remove(msg1)
        # proof that msg1 was received the third time
        self.assertIn(msg1, self._received_messages)
        self._received_messages.remove(msg1)
        # proof that msg1 was not received more than three times
        self.assertNotIn(msg1, self._received_messages)
        self.assertNotIn(msg2, self._received_messages)
