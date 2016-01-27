"""

    User support

"""


class User(object):

    """ User class

    Represents the logged in User

    """

    def __init__(self, name='Guest', **kwargs):
        super().__init__(**kwargs)
        self.name = name
