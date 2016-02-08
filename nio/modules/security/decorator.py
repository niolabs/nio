"""

    Common API Security

"""
import threading
from nio.modules.security.task import SecureTask
from nio.modules.security.authorizer import Authorizer, Unauthorized


class protected_access(object):

    """ Decorator to add to a method to protect access

    Retrieve user from current thread and evaluate access
    """

    def __init__(self, *tasks, meet_all=True):
        self._tasks = [task if isinstance(task, SecureTask)
                       else SecureTask(task)
                       for task in tasks]
        self._meet_all = meet_all

    def __call__(self, f):
        def wrapped_f(*args):
            # retrieve user
            thread = threading.current_thread()
            user = getattr(thread, "user", None)
            if user is None:
                raise Unauthorized()

            # evaluate all of the tasks
            Authorizer.authorize_multiple(
                user, *self._tasks, meet_all=self._meet_all)
            return f(*args)
        return wrapped_f


def _set_user(user):
    setattr(threading.current_thread(), "user", user)
