from nio.modules.security.authenticator import Authenticator
from nio.modules.security.authorizer import Authorizer
from nio.modules.module import Module


class SecurityModule(Module):

    def proxy_authenticator_class(self, authn_class):
        Authenticator.proxy(authn_class)

    def proxy_authorizer_class(self, authz_class):
        Authorizer.proxy(authz_class)

    def finalize(self):
        Authenticator.unproxy()
        Authorizer.unproxy()
        super().finalize()

    def get_module_order(self):
        return 30
