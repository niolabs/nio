class Request(object):

    """ Encapsulates web request information

    Create a Request instance to include web request parameters

    """

    def __init__(self, body, params, headers):
        """ Create a new Request instance.

        Args:
            body: request body
            params: request params
            headers: request headers

        """
        self._identifier = params.get('identifier')
        self._body = body
        self._params = params

        self._headers = headers

    def get_body(self):
        """ Retrieves request body

        Returns:
            Request body

        """
        return self._body

    def get_identifier(self):
        """ Retrieves request identifier

        Returns:
            Request identifier

        """
        return self._identifier

    def get_params(self):
        """ Retrieves request params

        Returns:
            Request params

        """
        return self._params

    def get_header(self, header, default=None):
        """ Retrieves request headers

        Returns:
            Request headers

        """
        return self._headers.get(header, default)
