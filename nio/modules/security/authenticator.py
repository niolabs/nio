"""

  Authenticator Interface

"""
from nio.modules.proxy import ModuleProxy


class Authenticator(ModuleProxy):

    """ Authenticator """

    @classmethod
    def authenticate(cls, request):
        """ Authenticate a request and return a User """
        raise NotImplementedError()
