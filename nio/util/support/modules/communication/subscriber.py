from nio.util.support.modules.communication import PubSubManager


class Subscriber(object):

    """ This class encapsulates the user-facing interface to NIO's
    subscriber.
    """
    def __init__(self, handler, matching_provider=None, **topics):
        self.handler = handler
        self.topics = topics

    def open(self):
        """ Subscribes handler to matching publishers

        """
        PubSubManager.add_subscriber(self)

    def close(self):
        """ Closes publisher.

        This method delegates functionality to notify others the
        subscriber removal via a management signal.

        """
        PubSubManager.remove_subscriber(self)
