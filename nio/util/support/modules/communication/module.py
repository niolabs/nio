from nio.util.support.modules.communication.publisher import Publisher
from nio.util.support.modules.communication.subscriber import Subscriber
from nio.modules.communication.module import CommunicationModule


class TestingCommunicationModule(CommunicationModule):

    def initialize(self, context):
        super().initialize(context)
        self.proxy_publisher_class(Publisher)
        self.proxy_subscriber_class(Subscriber)

    def finalize(self):
        super().finalize()
