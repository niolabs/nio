from nio.modules.web import WebServer
from nio.util.support.test_case import NIOTestCaseNoModules


class TestWebServer(NIOTestCaseNoModules):

    def test_web_server(self):
        """ Asserts web server bare functionality """
        web_server = WebServer()

        self.assertIsNone(web_server.host)
        self.assertIsNone(web_server.port)

        with self.assertRaises(NotImplementedError):
            web_server.add_handler(None)
        with self.assertRaises(NotImplementedError):
            web_server.start(None)
        with self.assertRaises(NotImplementedError):
            web_server.stop()
