from nio.testing.modules.communication.manager import PubSubManager


class Publisher(object):

    """ A version of a Publisher useful for unit-testing """

    def __init__(self, context=None, **topics):
        self.topics = topics

    def open(self):
        """ Opens publishing channel

        This method delegates functionality to notify others the
        publisher creation and its definitions via a management signal.

        """
        PubSubManager.add_publisher(self)

    def send(self, signals):
        """ Sends signals

        Args:
            signals: Signals to send
        """
        PubSubManager.send(self, signals)

    def close(self):
        """ Closes publisher.

        This method delegates functionality to notify others the
        publisher removal via a management signal.

        """
        PubSubManager.remove_publisher(self)

    def is_closed(self):
        """ Finds out if publisher has been closed """
        return self in PubSubManager.publishers
