
from nio.modules.proxy import ModuleProxy


class PublisherError(Exception):
    pass


class Publisher(ModuleProxy):

    """ An interface for a generic Publisher in the communication module """

    def __init__(self, context=None, **topics):
        """ Create a new publisher instance.

        Args:
            context: Information that can optionally be provided specific to
                the communication implementation.

                It can be used to customize a publisher by overriding settings
                such as 'heartbeat_interval' and 'heartbeat_check_interval'.

            topics: Key value pairs defining the kind of information to be
                published.
        """
        super().__init__(context, **topics)

    def open(self):
        """ Opens publishing channel

        This method will setup the channel for sending, it is implementation
        specific, for example in a tcp like implementation it will open a port.

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

        No further signals will be sent after a publisher is closed.

        """
        raise NotImplementedError()

    def is_closed(self):
        """ Finds out if publisher has been closed

        """
        raise NotImplementedError()
