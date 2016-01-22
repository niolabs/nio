from nio.modules.security.auth import Authenticator
from nio.modules.security.permissions import PermissionsProvider
from nio.modules.security.roles import RolesProvider
from nio.modules.module import Module


class SecurityModule(Module):

    def proxy_auth_class(self, auth_class):
        Authenticator.proxy(auth_class)

    def proxy_permissions_class(self, permissions_class):
        PermissionsProvider.proxy(permissions_class)

    def proxy_roles_class(self, roles_class):
        RolesProvider.proxy(roles_class)

    def finalize(self):
        Authenticator.unproxy()
        RolesProvider.unproxy()
        PermissionsProvider.unproxy()
        super().finalize()

    def get_module_order(self):
        return 30
