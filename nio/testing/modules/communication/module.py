from nio.testing.modules.communication.publisher import Publisher
from nio.testing.modules.communication.subscriber import Subscriber
from nio.modules.communication.module import CommunicationModule


class TestingCommunicationModule(CommunicationModule):

    """ A version of the communication module used for unit tests.

    This will proxy the Publisher and Subscriber classes that are also
    used for unit tests. These perform the pub/sub opertaions in memory.
    """

    def initialize(self, context):
        super().initialize(context)
        self.proxy_publisher_class(Publisher)
        self.proxy_subscriber_class(Subscriber)

    def finalize(self):
        super().finalize()
