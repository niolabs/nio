from nio.modules.proxy import ModuleProxy


class Subscriber(ModuleProxy):

    """ This class encapsulates the user-facing interface to NIO's
    subscriber.
    """

    def __init__(self, handler, matching_provider=None, **topics):
        """ Subscriber constructor
        Kwargs:
            Arguments describing kind of signals to subscribe to
        """
        super().__init__(handler, matching_provider, **topics)

    def open(self):
        """ Subscribes handler to matching publishers

        """
        raise NotImplementedError()

    def close(self):
        """ Closes publisher.

        This method delegates functionality to notify others the
        subscriber removal via a management signal.

        """

        raise NotImplementedError()
