
from nio.util.cache import Cache


class LogCache(object):

    """ A cache of log messages to prevent logging loops.

    Maintains logging instructions per code source line helping
    avoid potential infinite loops when logging from a logging handler
    subscriber.

    The criteria consists of determining if a log record from the same
    source code line and with the same message is in the Cache.
    """

    def __init__(self, expire_interval):
        """ Create a new LogCache instance.

        Args:
            expire_interval (seconds): how long an entry is kept in cache

        """
        self._cache = Cache(expire_interval)

    def process_record(self, record):
        """ Processes a record determining if it is present and add to cache

        Args:
            record: log record as incoming from logging module

        Returns:
            True: if record is present in cache
        """

        present = False

        # determine key and attempt to get record
        key = "{0}-{1}".format(record.filename, record.lineno)
        log_record = self._cache.get(key)

        # determine if item with same message is present
        if log_record and log_record.msg == record.msg:
            present = True

        # record is always added or updated in cache under given key
        try:
            self._cache.add(key, record)
        except NotImplementedError:
            # catch any potential errors arising from the fact that
            # logging module starts before any other, i.e., scheduling
            pass

        return present
