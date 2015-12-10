"""

  Web classes

"""


class Request(object):

    def __init__(self, body, params, headers):
        self._identifier = params.get('identifier')
        self._body = body
        self._params = params

        self._headers = headers

    def get_body(self):
        return self._body

    def get_identifier(self):
        return self._identifier

    def get_params(self):
        return self._params

    def get_header(self, header, default=None):
        return self._headers.get(header, default)


class Response(object):

    def set_header(self, header_name, header_value):
        raise NotImplementedError()

    def set_status(self, status, message=None):
        raise NotImplementedError()

    def set_body(self, body):
        raise NotImplementedError()


class HTTPError(Exception):

    def __init__(self, status=500, message=None):
        super().__init__()
        self.status = status
        self.message = message


class HTTPNotImplemented(HTTPError):

    """Exception raised for not implemented features."""

    def __init__(self):
        super().__init__(501, "Not Implemented")


class HTTPUnauthorized(HTTPError):

    """Exception raised for not authorized."""

    def __init__(self):
        super().__init__(401, "Unauthorized")


class HTTPNotFound(HTTPError):

    """Exception raised for not found errors."""

    def __init__(self):
        super().__init__(404, "Not Found")
