
class WebEngine():

    @classmethod
    def get(cls, port, host, config=None):
        pass

    @classmethod
    def remove_server(cls, server):
        pass

    @classmethod
    def get_servers(cls):
        pass

    @classmethod
    def configure(cls, configuration):
        """ Configure Web Server """
        pass

    @classmethod
    def get_name(cls):
        """ Returns server name """
        pass

    @classmethod
    def get_version(cls):
        """ Returns web server version """
        pass

    @classmethod
    def start(cls, callback=None):
        """ Starts Web Server using configured params """
        pass

    @classmethod
    def stop(cls):
        """ Stops running Web Servers """
        pass

    @classmethod
    def block(cls):
        """ Blocks the Web Server until further request arrives """
        pass
