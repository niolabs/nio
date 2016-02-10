class WebServer(object):
    """ Web Server

    Serves HTTP requests given a host, port, and additional configuration

    """

    @property
    def host(self):
        """ Provides server host """
        return None

    @property
    def port(self):
        """ Provides server port """
        return None

    def add_handler(self, handler):
        """ Adds a web handler

        Args:
            handler (WebHandler): Web handler

        """
        raise NotImplementedError()

    def start(self, configuration):
        """ Starts web server

        Args:
            configuration: Server configuration

        """
        raise NotImplementedError()

    def stop(self):
        """ Stops web server

        """
        raise NotImplementedError()
