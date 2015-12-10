from nio.modules.security.user import User


class Authenticator(object):

    def __init__(self, configuration=None):
        pass

    def authenticate(self, **kwargs):
        return User()
