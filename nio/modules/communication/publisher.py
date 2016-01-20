
from nio.modules.proxy import ModuleProxy


class PublisherError(Exception):
    pass


class Publisher(ModuleProxy):

    """ This class encapsulates the user-facing interface to NIO's
    publisher.
    """

    def __init__(self, context=None, **topics):
        """ Publisher constructor
        Kwargs:
            Arguments describing kind of signals to be published
        """
        super().__init__(context, **topics)

    def open(self):
        """ Opens publishing channel

        This method delegates functionality to notify others the
        publisher creation and its definitions via a management signal.

        """
        raise NotImplementedError()

    def send(self, signals):
        """ Sends signals

        Args:
            signals: Signals to send
        """

        raise NotImplementedError()

    def close(self):
        """ Closes publisher.

        This method delegates functionality to notify others the
        publisher removal via a management signal.

        """
        raise NotImplementedError()

    def is_closed(self):
        """ Finds out if publisher has been closed """
        raise NotImplementedError()
