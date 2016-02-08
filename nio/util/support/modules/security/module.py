from nio.util.support.modules.security.authenticator import Authenticator
from nio.util.support.modules.security.authorizer import Authorizer
from nio.modules.security.module import SecurityModule


class TestingSecurityModule(SecurityModule):

    def initialize(self, context):
        super().initialize(context)
        self.proxy_authenticator_class(Authenticator)
        self.proxy_authorizer_class(Authorizer)
