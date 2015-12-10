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
        if not cls._initialized:
            # proxy initialization happens only once
            cls._topics = topics
            cls._initialized = True

    @classmethod
    def finalize(cls):
        cls._initialized = False

    @classmethod
    def publish(cls, signals):
        cls._ensure_publisher_ready()
        # if all conditions to publish are met
        if cls._publisher_ready:
            with cls._publisher_lock:
                cls._publisher.send(signals)
            return

    @classmethod
    def close(cls):
        # reset publisher
        if cls._publisher:
            try:
                cls._publisher.close()
            except:
                pass
            finally:
                cls._publisher = None
                cls._publisher_ready = False
        cls.finalize()

    @classmethod
    def _ensure_publisher_ready(cls):
        # attempts to create Publisher, which will happen successfully when
        # interface gets proxy applied
        if not cls._publisher_ready:
            try:
                cls._publisher = Publisher(**cls._topics)
                cls._publisher.open()
                cls._publisher_ready = True
            except:
                return
