class Response(object):

    """ Encapsulates web response information

    Create a Response instance to include web response information

    """

    def set_header(self, header_name, header_value):
        """ Sets a single HTTP header.

        Args:
            header_name: header name
            header_value: header value

        """
        raise NotImplementedError()

    def set_status(self, status, message=None):
        """ Sets a web response status.

        Args:
            status: http status
            message: optional message

        """
        raise NotImplementedError()

    def set_body(self, body):
        """ Sets a web response body.

        Args:
            body: response body

        """
        raise NotImplementedError()
