from .test_publisher import TestPublisherBase


class TestPublisherNoCache(TestPublisherBase):

    def get_cache_interval(self):
        return 0

    def test_log_to_publisher_no_cache(self):
        msg1 = "warning message1 nocache"
        msg2 = "warning message2 nocache"
        warning_messages = [msg1, msg2, msg1]
        for message in warning_messages:
            self._publisher_logger.warning(message)

        for message in warning_messages:
            self.assertIn(message, self._received_messages)
            # make sure every message intended made it
            self._received_messages.remove(message)
