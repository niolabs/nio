from nio.modules.proxy import ModuleProxy


class WebEngine(ModuleProxy):

    @classmethod
    def get(cls, port, host, configuration=None):
        """ Instantiates a web server

        Args:
            port (int): Port listening for requests
            host (str): Web server host address.
            configuration (dict): Contains additional server configuration,
                might contain additional ssl settings such as:
                ssl_certificate, ssl_private_key, ssl_certificate_chain

        Returns:
            The server if it already exists, or a new instantiated server

        Raises:
            TypeError if there port is None

        """
        raise NotImplementedError()

    @classmethod
    def remove_server(cls, server):
        """ Stops and remove a server

        Args:
            server (WebServer): Server to remove

        """
        raise NotImplementedError()

    @classmethod
    def get_servers(cls):
        """ Provides a list of running web servers """
        raise NotImplementedError()

    @classmethod
    def configure(cls, configuration):
        """ Configure Web Engine

        Args:
            configuration: Engine configuration
        """
        raise NotImplementedError()

    @classmethod
    def get_name(cls):
        """ Provides engine name """
        raise NotImplementedError()

    @classmethod
    def get_version(cls):
        """ Provides engine version """
        raise NotImplementedError()

    @classmethod
    def start(cls, callback=None):
        """ Starts Web engine

        Starts a web engine based on previously set configuration

        Args:
            callback: optional engine entry point

        """
        raise NotImplementedError()

    @classmethod
    def stop(cls):
        """ Stops engine and running Web Servers """
        raise NotImplementedError()

    @classmethod
    def block(cls):
        """ Blocks the Web engine

        This method is normally called from the main thread to block
        execution since likely each request will be handled by a separate
        thread.

        When stopping the engine, it is expected for it wait for all currently
        executing requests/threads to terminate.

        """
        raise NotImplementedError()
