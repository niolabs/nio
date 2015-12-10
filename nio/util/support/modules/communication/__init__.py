from nio.modules.communication.matching.default import DefaultMatching


class PubSubManager(object):
    """ Helper class providing a simplistic support to
    'Publisher' and 'Subscriber' classes in support modules
    """

    publishers = {}
    subscribers = []

    @classmethod
    def add_publisher(cls, publisher):
        cls.publishers[publisher] = []
        for subscriber in cls.subscribers:
            if DefaultMatching.matches(subscriber.topics, publisher.topics):
                cls.publishers[publisher].append(subscriber)

    @classmethod
    def remove_publisher(cls, publisher):
        del cls.publishers[publisher]

    @classmethod
    def add_subscriber(cls, subscriber):
        cls.subscribers.append(subscriber)
        for publisher in cls.publishers.keys():
            if DefaultMatching.matches(subscriber.topics, publisher.topics):
                cls.publishers[publisher].append(subscriber)

    @classmethod
    def remove_subscriber(cls, subscriber):
        for publisher in cls.publishers.keys():
            try:
                cls.publishers[publisher].remove(subscriber)
            except:
                pass

    @classmethod
    def send(cls, publisher, signals):
        for subscriber in cls.publishers[publisher]:
            try:
                subscriber.handler(signals)
            except:
                pass
