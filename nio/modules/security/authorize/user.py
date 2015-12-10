"""

  Name Authorizer

"""
from nio.modules.security.authorize import Authorizer


def user_is(name):
    """ Validate user logged in matches
    """
    return UserAuthorizer(name).authorize


class UserAuthorizer(Authorizer):
    """ Validate user logged in matches
    """

    def __init__(self, name):
        """ Initialize Authorizer

        Args:
            name (str): User's name authorized
        """
        self._name = name

    def authorize(self, user):
        """ Authorize a user
        """
        return user.name == self._name
