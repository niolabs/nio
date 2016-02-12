"""

  Secure Command

"""
from nio.modules.security.authorizer import Authorizer, Unauthorized
from nio.command import Command


class SecureCommand(Command):

    """ Secure Command

    Command including conditions to verify before allowing to perform
    the command

    """

    def __init__(self, name, *tasks, title=None, meet_all=True):
        """

        Args:
            tasks (list) : task(s) to evaluate
        """
        super().__init__(name, title)
        self._tasks = tasks
        self._meet_all = meet_all

    def can_invoke(self, user):
        """ Returns if the user specified meets the conditions contained in
        this command

        """
        if user is None:
            return False
        try:
            Authorizer.authorize_multiple(
                user, *self._tasks, meet_all=self._meet_all)
            return True
        except Unauthorized:
            return False
