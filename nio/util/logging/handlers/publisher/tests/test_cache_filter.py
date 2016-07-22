from nio.testing.test_case import NIOTestCase
from nio.util.logging.handlers.publisher.cache_filter import CacheFilter
from nio.util.logging.handlers.publisher.tests import get_log_record_same_line


class TestCacheFilter(NIOTestCase):

    def test_cache_filter(self):
        """ Asserts that a CacheFilter can filter out repeated log messages """

        cache_filter = CacheFilter("test_cache_filter", expire_interval=1)

        msg1 = "message1 cached"
        msg2 = "message2 cached"

        self.assertTrue(cache_filter.filter(get_log_record_same_line(msg1)))
        self.assertTrue(cache_filter.filter(get_log_record_same_line(msg2)))

        # filtering same records result in them being rejected
        self.assertFalse(cache_filter.filter(get_log_record_same_line(msg1)))
        self.assertFalse(cache_filter.filter(get_log_record_same_line(msg2)))
