"""

    User support

"""
from threading import current_thread
from nio.util import ensure_list


def get_current_user():
    thread = current_thread()
    return getattr(thread, "user", None)


class User(object):
    """ User class

    Represents the logged in User and roles it may have

    """
    def __init__(self, name='Guest', roles='guest'):
        self._name = name
        self._roles = ensure_list(roles)

    @property
    def name(self):
        return self._name

    @property
    def roles(self):
        return self._roles

    def has_role(self, role):
        return role in self._roles
