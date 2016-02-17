import logging

from nio.util.logging.handlers.publisher.cache import LogCache


class CacheFilter(logging.Filter):

    def __init__(self, name='', expire_interval=1):
        """ Create a new CacheFilter instance.

        Args:
            name: see parent class logging.Filter
            expire_interval (seconds): specifies how long an entry will be
             kept in the cache

        """
        super().__init__(name=name)
        self._log_cache = LogCache(expire_interval)

    def filter(self, record):
        """  Filters the record before being logged

        If the record is determined to be in the cache, it is filtered
        out.

        Args:
            record: record being filtered

        Returns:
            True if record should be logged, False otherwise.
        """
        return not self._log_cache.process_record(record)
