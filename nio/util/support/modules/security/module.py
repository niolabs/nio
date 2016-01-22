from nio.util.support.modules.security.auth import Authenticator
from nio.util.support.modules.security.permissions import PermissionsProvider
from nio.util.support.modules.security.roles import RolesProvider
from nio.modules.security.module import SecurityModule


class TestingSecurityModule(SecurityModule):

    def initialize(self, context):
        super().initialize(context)
        self.proxy_auth_class(Authenticator)
        self.proxy_permissions_class(PermissionsProvider)
        self.proxy_roles_class(RolesProvider)

        # TODO: Remove once security module is refactored
        from niocore.modules.security import SecurityModule as CoreSecModule
        CoreSecModule._reset({})
