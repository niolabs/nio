from nio.modules.security.user import User


class Authenticator(object):

    @classmethod
    def authenticate(cls, request):
        return User(name="test_user")
