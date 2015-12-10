from datetime import datetime


class LogRecord(object):

    """ Keeps track of last record logged for a given code source line
    """

    def __init__(self, time, msg):
        self.last_time = time
        self.msg = msg

    def __str__(self):
        return "last time: {0}, msg: {1}".format(self.last_time, self.msg)


class LogCache(object):

    """ Maintains logging instructions per code source line
            expire_time: determines how long a log entry is maintained to

    """

    def __init__(self, expire_interval):
        # dictionary where the key is formed combining file path and
        # line number
        self._logs = dict()
        # determines how long to keep an entry as "present"
        self._expire_interval = expire_interval

    def process_record(self, record):
        """ Processes a record determining if is present, when not, record
        is added automatically to the cache

        Args:
            record: log record as incoming from logging module

        Returns:
            True: if record is present in cache
        """

        # determine current time
        now = datetime.utcnow()

        # erase from cache expired logs before considering received record
        self._process_logs_expiration(now)

        # is it in the cache?
        present = False
        key = "{0}-{1}".format(record.filename, record.lineno)
        log_record = self._logs.get(key, None)
        if log_record:
            if log_record.msg == record.msg:
                present = True
            else:
                # update message for this entry
                self._logs[key].msg = record.msg
            # update time
            self._logs[key].last_time = now
        else:
            # from now on, it is present
            self._logs[key] = LogRecord(now, record.msg)

        return present

    def close(self):
        # erase cache
        self._logs = dict()

    def _process_logs_expiration(self, now):
        """ Remove expired logs
        Args:
            now: logs present after this time will be removed
        """
        keys_to_delete = [key for key in self._logs
                          if now >=
                          self._logs[key].last_time + self._expire_interval]
        for key in keys_to_delete:
            del self._logs[key]
