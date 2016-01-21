"""

  Permission Provider Interface

"""
from nio.modules.proxy import ModuleProxy


class PermissionsProvider(ModuleProxy):

    """ Provides permissions data
    """

    def __init__(self, data=None):
        """ Create a Permissions Provider """
        super().__init__(data)

    def get_permissions(self):
        raise NotImplementedError()
