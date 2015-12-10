from datetime import datetime
import logging


class NIOFilter(logging.Filter):

    def filter(self, record):
        """  Filter the record before being logged

        We add niotime and context properties to the record so loggers
        created before the Logging Module initialization can be written
        using nio formatter
        """
        if not hasattr(record, 'niotime'):
            record.niotime = self._time()
            record.context = record.name
        return True

    def _time(self):
        """ Generate a nicely formatted time string for a log entry

        Args:
            None

        Returns:
            A time string
        """

        now = datetime.utcnow()
        return '%d-%02d-%02d %02d:%02d:%02d.%03d' % (
            now.year, now.month, now.day,
            now.hour, now.minute, now.second,
            now.microsecond / 1000)
