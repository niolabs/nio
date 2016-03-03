from nio.modules.proxy import ModuleProxy


class Subscriber(ModuleProxy):

    """ An interface for a generic Subscriber in the communication module """

    def __init__(self, handler, matching_provider=None, **topics):
        """ Create a new subscriber instance.

        Args:
            handler: Specifies where signals will be received. A signature
                definition sample is provided below.

                def process_signals(self, signals)

            matching_provider: Matching provider which could optionally be
                specified to override system-wide setting.

            topics: Key value pairs defining the kind of information to be
                subscribed to.
        """
        super().__init__(handler, matching_provider, **topics)

    def open(self):
        """ Open a subscriber

        When opening a subscriber the system will look for matches against
        existing publishers, when a match is found, a 'connection' is made
        so that signals published by matching publisher are received by this
        subscriber

        """
        raise NotImplementedError()

    def close(self):
        """ Closes publisher.

        This method delegates functionality to notify others the
        subscriber removal via a management signal.

        """

        raise NotImplementedError()
