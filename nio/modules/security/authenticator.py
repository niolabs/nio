"""

  Authenticator Interface

"""
from nio.modules.proxy import ModuleProxy


class Authenticator(ModuleProxy):

    @classmethod
    def authenticate(cls, request):
        """ Authenticate a request and return a User.

        The objective of this method is to determine the user who is making a
        given web request. Most implementations will probably force the request
        object passed in to be an instance of Request from the web module.

        Args:
            request (Request): A request from the web module used to determine
                the user who is making this request

        Returns:
            User: A reference to the user making the request.

        Raises:
            Unauthorized: If it cannot determine the user making the request
        """
        raise NotImplementedError()
