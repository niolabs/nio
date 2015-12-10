"""

    Permissions based authorizer

"""
import re
from nio.modules.security.authorize import Authorizer
from nio.util import find
from nio.util import ensure_list


def has_permission(permissions):
    """ Validate user has any of all permissions

    """
    return PermissionAuthorizer(permissions).authorize


class PermissionAuthorizer(Authorizer):
    """ Validate user has any of all permissions

    """

    def __init__(self, permissions):
        """ Initializes an Authorizer based on permissions

        Args:
            permissions (str or list): Permissions allowed
        """
        self._permissions = ensure_list(permissions)

    @staticmethod
    def _get_provider_permissions():
        """ Retrieves dictionary containing permission data

        Example:
            {
                "admin": { "allow": [".*"] },
                "user": { "allow": [ "blocks.*"] },
                "guest": { "allow": ["services.view", "blocks.view"] }
            }
        """
        from niocore.modules.security import SecurityModule
        return SecurityModule.get_permissions_provider().get_permissions()

    def _get_permissions(self, list_settings, permission_type):
        """ Retrieve permissions in a lis of settings based ona a type

        Iterates through the list of permission settings and returns a
        list of the permissions related to a type

        Args:
            list_settings (list): List of permission settings
            permission_type (str): type of permission we want to filter by

        Example :

            list = [{"allow": "["delete", "edit"]},
                    {"allow": "["fetch"]},
                    {"deny":  "["create"]}]

            filter_list = self._get_permissions(list, "allow")

            filter_list = ["delete", "edit", "fetch"]

        """
        permission_list = []
        for setting in list_settings:
            filter_dict = setting.get(permission_type, None) \
                if setting else None
            if filter_dict:
                permission_list.extend(filter_dict)
        return permission_list

    def authorize(self, user):
        """ Authorize a user based on permissions

         Finds all permissions a user has based on its roles, then verifies
        if any of the user permissions matches the filter one included in
        this authorizer

        """
        # retrieve permissions in real time
        provider_permissions = self._get_provider_permissions() or {}
        # find out which permissions (roles) apply to this user
        user_settings = [provider_permissions.get(role, None)
                         for role in user.roles]
        if not len(user_settings):
            return False
        allows = self._get_permissions(user_settings, "allow")
        # Verify for allow access
        return self._verify_allow_access(allows) is not None

    def _verify_allow_access(self, permissions):
        """ Finds if there is a permission that matches the
        permissions provided

        Evaluates a list of permissions matching them again the list
        contained in this class

        Args:
            permissions (list): List of permission to match against the list
                contained in this class

        """
        return find(lambda p: self._match_permission(p), permissions)

    def _match_permission(self, permission):
        """ Checks if a permission matches any of the permissions in this
        authorize

        Args:
            permission (str): permission to match against this authorizer
        """
        return find(lambda p: re.match(permission, p), self._permissions)
