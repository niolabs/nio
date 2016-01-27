"""

  Authenticator Interface

"""
from nio.modules.proxy import ModuleProxy


class Authenticator(ModuleProxy):

    """ Authenticator """

    def __init__(self):
        """ Create an Authenticator """
        super().__init__()

    def authenticate(self, request):
        """ Authenticate a request and return a User """
        raise NotImplementedError()
