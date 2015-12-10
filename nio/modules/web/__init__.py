"""

    Web Module Initialization

"""
from nio.modules.proxy import ModuleProxy, proxied
from nio.common.command.security import SecureCommand
from nio.modules.security.permissions.authorizer import has_permission
from nio.modules.security.condition import SecureCondition


class WebHandler(object):

    def __init__(self, route):
        self.route = route

    def handle(self, request, response):
        raise NotImplementedError()


class StaticHandler(WebHandler):

    def __init__(self, route):
        super().__init__(route)

    def handle(self, request, response):
        raise NotImplementedError()


class RESTHandler(WebHandler):

    def __init__(self, route):
        super().__init__(route)
        self._set_security()

    def is_collection(self):
        return False

    def on_get(self, request, response):
        raise NotImplementedError()

    def on_post(self, request, response):
        raise NotImplementedError()

    def on_put(self, request, response):
        raise NotImplementedError()

    def on_delete(self, request, response):
        raise NotImplementedError()

    def on_options(self, request, response):
        raise NotImplementedError()

    def _set_security(self):
        self.commands = \
            [SecureCommand(api_endpoint,
                           SecureCondition(name, True,
                                           has_permission(permissions)))
             for (api_endpoint, name, permissions) in
             self.get_security_descriptors()]

    @staticmethod
    def get_security_descriptors():
        """ To be overriden by handlers securing their endpoints

        Returns:
            list of tuples with following format:
                (api_endpoint (str), name (str), permissions (str))
        """
        return []


class WebServer(object):

    @property
    def host(self):
        return None

    @property
    def port(self):
        return None

    def add_handler(self, handler):
        raise NotImplementedError()

    def start(self, module_conf):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()


class WebEngine(ModuleProxy):

    @classmethod
    @proxied
    def get(cls, port, host, config=None):
        raise NotImplementedError()

    @classmethod
    @proxied
    def remove_server(cls, server):
        raise NotImplementedError()

    @classmethod
    @proxied
    def get_servers(cls):
        raise NotImplementedError()

    @classmethod
    @proxied
    def configure(cls, configuration):
        """ Configure Web Server """
        raise NotImplementedError()

    @classmethod
    @proxied
    def get_name(cls):
        """ Returns server name """
        raise NotImplementedError()

    @classmethod
    @proxied
    def get_version(cls):
        """ Returns web server version """
        raise NotImplementedError()

    @classmethod
    @proxied
    def start(cls, callback=None):
        """ Starts Web Server using configured params """
        raise NotImplementedError()

    @classmethod
    @proxied
    def stop(cls):
        """ Stops running Web Servers """
        raise NotImplementedError()

    @classmethod
    @proxied
    def block(cls):
        """ Blocks the Web Server until further request arrives """
        raise NotImplementedError()
