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


# A user service account that represents the core process
class CoreServiceAccount(User):
    def __init__(self):
        super().__init__(name='Core Service Account')
