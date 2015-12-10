"""

    Role Authorizer

"""
from nio.modules.security.authorize import Authorizer
from nio.util import ensure_list


def in_role(roles, all_roles=False):
    """ Validates current user logged in belongs to a role
    """
    return RoleAuthorizer(roles).authorize


class RoleAuthorizer(Authorizer):
    """ Validates current user logged in belongs to a role
    """

    def __init__(self, roles, all_roles=False):
        """ Initialize Role Authorizer

        Args:
            roles (list): list of roles authorized
            all_roles (bool): Flag indicating the user must have ALL roles
        """
        roles = roles or []
        self._roles = ensure_list(roles)
        self._all_roles = all_roles

    def authorize(self, user):
        """ Authorize a user
        """
        if self._all_roles:
            # check if all roles must be present
            return set(self._roles) <= set(user.roles)
        # any of the roles is fine
        return not set(user.roles).isdisjoint(self._roles)
