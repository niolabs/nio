class HTTPError(Exception):

    def __init__(self, status=500, message=None, body=None):
        """ Create a new HTTPError instance.

        Args:
            status: http error status
            message: http optional error message
            body (dict): An optional dictionary to include in the response
        """
        super().__init__()
        self.status = status
        self.message = message
        self.body = body


class HTTPNotImplemented(HTTPError):

    """Exception raised for not implemented features."""

    def __init__(self):
        """ Create a new HTTPNotImplemented instance.
        """
        super().__init__(501, "Not Implemented")


class HTTPUnauthorized(HTTPError):

    """Exception raised for not authorized."""

    def __init__(self):
        """ Create a new HTTPUnauthorized instance.
        """
        super().__init__(401, "Unauthorized")


class HTTPNotFound(HTTPError):

    """Exception raised for not found errors."""

    def __init__(self):
        """ Create a new HTTPNotFound instance.
        """
        super().__init__(404, "Not Found")
