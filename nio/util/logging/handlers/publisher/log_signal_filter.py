import logging

from nio.util.logging.handlers.publisher.log_signal import LogSignal


class LogSignalFilter(logging.Filter):

    def filter(self, record):
        """  Filters out LogSignal records

        Args:
            record: record being filtered

        Returns:
            True if record should be logged, False otherwise.
        """
        return not isinstance(record.msg, LogSignal)
