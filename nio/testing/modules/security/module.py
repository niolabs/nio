from nio.testing.modules.security.authenticator import Authenticator
from nio.testing.modules.security.authorizer import Authorizer
from nio.modules.security.module import SecurityModule


class TestingSecurityModule(SecurityModule):

    def initialize(self, context):
        super().initialize(context)
        self.proxy_authenticator_class(Authenticator)
        self.proxy_authorizer_class(Authorizer)
