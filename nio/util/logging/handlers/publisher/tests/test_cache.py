import inspect
from datetime import timedelta
from time import sleep

from ..cache import LogCache
from nio.util.support.test_case import NIOTestCaseNoModules


class LogRecord(object):

    def __init__(self, filename, lineno, msg):
        self.filename = filename
        self.lineno = lineno
        self.msg = msg


def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno


class TestCache(NIOTestCaseNoModules):

    def test_cache(self):
        """ Asserts that cache from different lines removes elements
        as expected
        """
        log_cache = LogCache(timedelta(seconds=0.1))

        # when logging from different lines, message text is not relevant
        record1 = LogRecord(__file__, lineno(), "1")
        record2 = LogRecord(__file__, lineno(), "1")
        self.assertFalse(log_cache.process_record(record1))
        self.assertFalse(log_cache.process_record(record2))

        sleep(0.06)
        # this updates the time of the log record in the cache
        self.assertTrue(log_cache.process_record(record1))

        sleep(0.06)
        # assert that is gone, and puts it back in
        self.assertFalse(log_cache.process_record(record2))

        sleep(0.06)
        self.assertFalse(log_cache.process_record(record1))
        # assert that record2 was put back in
        self.assertTrue(log_cache.process_record(record2))

        log_cache.close()

    def test_cache_same_line(self):
        """ Asserts that cache from same line removes/updates elements
        as expected
        """
        log_cache = LogCache(timedelta(seconds=0.1))

        record1 = self._get_log_record("1")
        record2 = self._get_log_record("2")
        self.assertFalse(log_cache.process_record(record1))
        self.assertFalse(log_cache.process_record(record2))

        # they are not present because the message changes every time
        self.assertFalse(log_cache.process_record(record1))
        self.assertFalse(log_cache.process_record(record2))

        # assert that when message doesn't change, it is present
        self.assertTrue(log_cache.process_record(record2))
        # give it time, and assert that it is gone
        sleep(0.11)
        self.assertFalse(log_cache.process_record(record2))

        log_cache.close()

    def _get_log_record(self, msg):
        return LogRecord(__file__, lineno(), msg)
