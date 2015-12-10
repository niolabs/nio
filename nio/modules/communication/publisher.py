
from nio.modules.proxy import ModuleProxy, proxied


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

    @proxied
    def open(self):
        """ Opens publishing channel

        This method delegates functionality to notify others the
        publisher creation and its definitions via a management signal.

        """
        raise NotImplementedError()

    @proxied
    def send(self, signals):
        """ Sends signals

        Args:
            signals: Signals to send
        """

        raise NotImplementedError()

    @proxied
    def close(self):
        """ Closes publisher.

        This method delegates functionality to notify others the
        publisher removal via a management signal.

        """
        raise NotImplementedError()

    @proxied
    def is_closed(self):
        """ Finds out if publisher has been closed
        """
        raise NotImplementedError()
