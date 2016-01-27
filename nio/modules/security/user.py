"""

    User support

"""
from threading import current_thread


def get_current_user():
    thread = current_thread()
    return getattr(thread, "user", None)


class User(object):

    """ User class

    Represents the logged in User and roles it may have

    """

    def __init__(self, name='Guest'):
        self.name = name
