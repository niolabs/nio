import logging
from datetime import datetime

from nio.util.logging.handlers.publisher.log_signal import LogSignal
from nio.util.logging.handlers.publisher.proxy import PublisherProxy


class PublisherHandler(logging.Handler):

    """ Publisher handler for logging.

    Publishers log events using the nio Publisher interface therefore
    allowing reception of log events through the network through the
    instantiation of Subscribers

    Instances of this class will be registered with the base Logger on an
    as-needed basis.

    Users of this handler should be aware of the potential risk of issuing
    logging statements within the Subscriber catching signals published through
    this handler, therefore, logging within the subscriber 'handler' is
    not recommended.

    """

    def __init__(self, topics={"type": ["logging"]}):
        """  Create a new PublisherHandler instance.

        Args:
            topics: topics to use when publishing log messages

        """
        super().__init__()

        # Initialize unique proxy for all publisher handlers.
        PublisherProxy.init(topics)

    def emit(self, record):
        """ Publish the log record on the opened publisher

        Args:
            record (LogRecord): record to be logged.

        Returns:

        """
        try:
            # publishing it as a signal
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
        """ Closes handler

        Releases/Closes any resources used by handler

        """
        # close all dependencies
        PublisherProxy.close()

        super().close()
