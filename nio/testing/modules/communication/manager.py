from nio.modules.communication.matching.default import DefaultMatching


class PubSubManager(object):

    """ A Communication manager to allow simple pub/sub in unit tests

    This works with the unit-test Publisher and Subscriber to allow data
    to be published and subscribed to in the same process.
    """

    publishers = {}
    subscribers = []

    @classmethod
    def add_publisher(cls, publisher):
        """ Add a publisher to this manager.

        This will register the topics of the publisher with any matching
        Subscribers so that they will get called when data is published on
        this publisher.
        """
        cls.publishers[publisher] = []
        for subscriber in cls.subscribers:
            if DefaultMatching.matches(subscriber.topics, publisher.topics):
                cls.publishers[publisher].append(subscriber)

    @classmethod
    def remove_publisher(cls, publisher):
        """ De-register a publisher with this manager """
        if publisher in cls.publishers:
            del cls.publishers[publisher]

    @classmethod
    def add_subscriber(cls, subscriber):
        """ Add a subscriber to this manager and subscribe to relevant data.

        This will add this subscriber's callback to any registered publishers
        whose topics match.
        """
        cls.subscribers.append(subscriber)
        for publisher in cls.publishers.keys():
            if DefaultMatching.matches(subscriber.topics, publisher.topics):
                cls.publishers[publisher].append(subscriber)

    @classmethod
    def remove_subscriber(cls, subscriber):
        """ De-register the subscriber with this manager """
        for publisher_callbacks in cls.publishers.values():
            if subscriber in publisher_callbacks:
                publisher_callbacks.remove(subscriber)

    @classmethod
    def send(cls, publisher, signals):
        """ Send data from a publisher to any subscribed callbacks """
        for subscriber in cls.publishers[publisher]:
            subscriber.handler(signals)
