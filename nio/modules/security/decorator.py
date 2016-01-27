"""

    Common API Security

"""
import threading
from nio.modules.security import Unauthorized
from nio.modules.security.permissions.authorizer import has_permission
from nio.modules.security.condition import SecureCondition
from nio.util import ensure_is


class protected_access(object):

    """ Decorator to add to a method to protect access

    Retrieve user from current thread and evaluate access
    """

    def __init__(self, permissions, meet_all=True):
        permissions = ensure_is(permissions, [list, tuple], lambda x: [x])
        self._condition = SecureCondition("unused", meet_all,
                                          [has_permission(permission)
                                           for permission in permissions])

    def __call__(self, f):
        def wrapped_f(*args):
            # retrieve user
            thread = threading.current_thread()
            user = getattr(thread, "user", None)
            # evaluate conditions
            if not user or not self._condition.evaluate(user):
                raise Unauthorized()
            return f(*args)
        return wrapped_f
