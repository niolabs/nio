"""
   NIO web support base class

"""
import requests
import json
from nio.testing.test_case import NIOTestCase
from nio.modules.web import WebEngine


class NIOWebTestCase(NIOTestCase):

    """ Base Unit Test case class for Web related tests.

    Allows tests to concisely interact with the WebEngine
    and the requests module. Abstracts away some otherwise inevitable
    boilerplate.

    Add and remove servers as needed, specifying endpoint and config
    values. Check the status and contents of responses to requests
    made against those servers by name without ever touching the
    underlying response object.

    Example:
    server = self.add_server("foo", {"socket_port": 8182})
    server.add_handler(SomeHandler(<route>, <target>))
    self.start_engine()

    target = "http://%s:%d/foo" % (self.get_conf_host(), self.get_conf_port())
    self.assertResponseStatus('GET', target, 200)

    The above example adds a server and a handler, starts the CherryPy engine,
    and confirms that a GET request to the appropriate url returns HTTP Status
    Code 200.

    """

    def get_test_modules(self):
        """ Adds 'web' and 'security' to default modules """
        return super().get_test_modules() | {'web', 'security'}

    def setUp(self):
        super().setUp()
        # Check Servers were removed between tests
        self.assertEqual(0, len(WebEngine.get_servers()))
        self.servers = []

    def tearDown(self):
        for server in list(self.servers):
            self.remove_server(server)
        self.assertEqual(0, len(WebEngine.get_servers()))
        super().tearDown()

    def start_engine(self, callback=None):
        """ Starts the web engine

        Args:
            callback: optional engine entry point

        """
        WebEngine.start(callback)

    def add_server(self, port, config=None, host="127.0.0.1", auto_start=True):
        """ Adds and starts a web server (if auto_start is True)

        Args:
            port (int): web server port
            config (dict): server configuration parameters
            host (str): web server host
            auto_start (bool): if True server is started

        """
        web_server = WebEngine.get(port, host,
                                   config if config is not None else {})
        self.servers.append(web_server)
        if auto_start:
            web_server.start()
        return web_server

    def remove_server(self, server):
        """ Removes a web server

        Args:
            server: web server

        """
        self.servers.remove(server)
        WebEngine.remove_server(server)

    def get_conf_host(self):
        """ Returns default host """
        return '127.0.0.1'

    def get_conf_port(self):
        """ Returns default port """
        return 8181

    def get_response(self, method, url, **kwargs):
        """ Get a response object for a given resource

        Args:
            method (str): e.g. GET, POST, etc.
            url (str): Complete target for the request
            kwargs (dict): Payload for POST/PUT

        """
        return requests.request(method, url, **kwargs)

    def assertResponseStatus(self, method, url, status, **kwargs):
        """ Checks that the specified request returns the specified status.

        Args:
            method (str): e.g. GET, POST, etc.
            url (str): Complete target for the request
            status (int): The expected status for the response.
            kwargs (dict): Payload for POST/PUT

        """
        response = self.get_response(method, url, **kwargs)
        self.assertEqual(response.status_code, status)

    def assertResponseJSON(self, method, url, key, value=None, data=None):
        """ Assert that the specified response returns a JSON with a value

        Args:
            method (str): e.g. GET, POST, etc.
            url (str): Complete target for the request
            key (str): The JSON response is expected to contain this key.
            value (str): If set, asserts that (key, value) is in the response.
            data (str): Payload for POST/PUT requests.

        """
        response = self.get_response(method, url, data=data)
        data = json.loads(response.text)
        if value is not None:
            self.assertEqual(data[key], value)
        else:
            self.assertIn(key, data)

    def assertResponseJSONValue(self, method, url, value, data=None,
                                status=200):
        """ Assert that the specified response returns a JSON matching a value

        Args:
            method (str): e.g. GET, POST, etc.
            url (str): Complete target for the request
            value (dict): Expected Http Response
            data (str): Payload for POST/PUT requests.

        """
        response = self.get_response(method, url, data=data)
        self.assertEqual(response.status_code, status)
        data = json.loads(response.text)
        self.assertDictEqual(data, value)
