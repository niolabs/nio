"""

  Authenticator Interface

"""
from nio.modules.proxy import ModuleProxy, proxied


class Authenticator(ModuleProxy):

    """ Authenticator """
    # Note: We don't proxy a constructor, the ModuleProxy __init__ will handle
    # the mapping to the proper class for us, so just call super

    def __init__(self, configuration=None):
        """ Create an Authenticator based on a configuration  """
        super().__init__(configuration)

    @proxied
    def authenticate(self, **kwargs):
        raise NotImplementedError()
