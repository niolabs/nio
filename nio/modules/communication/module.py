from nio.modules.communication.publisher import Publisher
from nio.modules.communication.subscriber import Subscriber
from nio.modules.module import Module


class CommunicationModule(Module):

    def proxy_publisher_class(self, publisher_class):
        Publisher.proxy(publisher_class)

    def proxy_subscriber_class(self, subscriber_class):
        Subscriber.proxy(subscriber_class)

    def finalize(self):
        Publisher.unproxy()
        Subscriber.unproxy()
        super().finalize()

    def get_module_order(self):
        return 50
