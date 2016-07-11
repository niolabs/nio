from nio import Signal
from nio.testing.test_case import NIOTestCase
from nio.util.logging.handlers.publisher.log_signal_filter import \
    LogSignalFilter
from nio.util.logging.handlers.publisher.log_signal import LogSignal
from nio.util.logging.handlers.publisher.tests import LogRecordTest, lineno


class TestLogSignalFilter(NIOTestCase):

    def test_cache_filter(self):
        """ Asserts that a LogSignalFilter filters out records with LogSignal
        """

        log_signal_filter = LogSignalFilter()

        # creare LgSignal simulating its arguments
        log_signal =\
            LogSignal("time",
                      "context",
                      "level",
                      "message",
                      "filename",
                      "function",
                      "line")
        # a record with a msg containing a LogSignal instance is filtered out
        self.assertFalse(log_signal_filter.filter(
            LogRecordTest(__file__, lineno(), log_signal)))

        # verify that it lets through otherwise
        self.assertTrue(log_signal_filter.filter(
            LogRecordTest(__file__, lineno(), Signal())))
