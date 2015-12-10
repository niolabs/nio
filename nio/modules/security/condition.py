"""

  Secure Condition

"""
from nio.util import ensure_is


class SecureCondition(object):

    """ Secure condition for performing operations

    Contains a set of conditions

    """

    def __init__(self, name, meet_all, conditions):
        if name is None:
            raise TypeError("name")
        if meet_all is None:
            raise TypeError("meet_all")
        if conditions is None:
            raise TypeError("conditions")
        self._name = name
        self._all = meet_all
        self._conditions = ensure_is(conditions, [list, tuple], lambda x: [x])

    def evaluate(self, user):
        """ Evaluate all conditions

        Evaluates all registered conditions and return True if
            _all is True and all return True  or
            _all is False and any returns True
        """
        val = False
        for condition in self._conditions:
            val = callable(condition) and condition(user)
            if self._all:
                if not val:
                    return False
            else:
                if val:
                    return val
        return val
