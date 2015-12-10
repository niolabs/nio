"""

  Secure Command

"""
from nio.common.command import Command


class SecureCommand(Command):

    """ Secure Command

    Command including conditions to verify before allowing to perform
    the command

    """

    def __init__(self, name, condition, title=None):
        """

        Args:
            condition (SecureCondition) : condition(s) to evaluate
        """
        super().__init__(name, title)
        self._condition = condition

    def can_invoke(self, user):
        """ Returns if the user specified meets the conditions contained in
        this command

        """
        if user is None:
            return False
        return self._condition.evaluate(user)
