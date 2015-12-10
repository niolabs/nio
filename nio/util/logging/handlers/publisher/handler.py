import logging
from datetime import datetime, timedelta

from .cache import LogCache
from .log_signal import LogSignal
from .proxy import PublisherProxy


class PublisherHandler(logging.Handler):

    def __init__(self, cache_expire_interval=1, topics={"type": ["logging"]}):
        super().__init__()
        PublisherProxy.init(topics)
        # a cache creation will eliminate a potential infinite loop that
        # can be created when a subscriber logs a message that is in turn
        # published through this handler
        self._log_cache = LogCache(timedelta(seconds=cache_expire_interval)) \
            if cache_expire_interval else None

    def emit(self, record):
        try:
            publish_record = True
            if self._log_cache:
                # if determined to be in cache, record is not published
                publish_record = not self._log_cache.process_record(record)
            if publish_record:
                # publish it as a signal
                signal = LogSignal(datetime.utcfromtimestamp(record.created),
                                   record.context,
                                   record.levelname,
                                   record.msg,
                                   record.filename,
                                   record.funcName,
                                   record.lineno)
                PublisherProxy.publish([signal])
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            pass

    def close(self):
        # close all dependencies
        PublisherProxy.close()
        if self._log_cache:
            self._log_cache.close()
        super().close()
