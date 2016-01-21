"""

  Roles Provider Interface

"""
from nio.modules.proxy import ModuleProxy


class RolesProvider(ModuleProxy):

    """ Provides roles functionality for some security Authenticators by
    providing roles for users
    """

    def __init__(self, data=None):
        """ Create a Roles Provider """
        super().__init__(data)

    def get_user_roles(self, user):
        raise NotImplementedError()
