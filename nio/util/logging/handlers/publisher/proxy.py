from threading import RLock

from nio.modules.communication.publisher import Publisher


class PublisherProxy(object):

    _publisher = None
    _publisher_lock = RLock()
    # establish that publisher is ready for use
    _publisher_ready = False
    # many loggers get initialized however, only once the proxy is initialized
    _initialized = False
    # publishing criteria
    _topics = {}

    @classmethod
    def init(cls, topics):
        """ Initializes the proxy

        Args:
            topics: topics to use when publishing signals

        """
        if not cls._initialized:
            # proxy initialization happens only once
            cls._topics = topics
            cls._initialized = True

    @classmethod
    def publish(cls, signals):
        """ Publishes logging signals.

        This method ensures that publisher is ready to send signals, it
        might happen that a call to publish 'logging' signals might come before
        publisher is ready since logging is initialized before communication


        Args:
            signals: signals to publish

        """
        cls._ensure_publisher_ready()
        # publish when all conditions are met
        if cls._publisher_ready:
            with cls._publisher_lock:
                cls._publisher.send(signals)

    @classmethod
    def close(cls):
        """ Closes publisher by releasing all resources """

        if cls._publisher:
            try:
                cls._publisher.close()
            except:
                pass
            finally:
                cls._publisher = None
                cls._publisher_ready = False
        cls._initialized = False

    @classmethod
    def _ensure_publisher_ready(cls):
        """ Ensures publisher is ready by attempting to create Publisher,
        which will happen successfully once communication module is initialized
        """
        if not cls._publisher_ready:
            try:
                cls._publisher = Publisher(**cls._topics)
                cls._publisher.open()
                cls._publisher_ready = True
            except:
                return
