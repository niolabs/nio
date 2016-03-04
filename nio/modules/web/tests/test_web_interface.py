from nio.modules.web import WebEngine
from nio.testing.test_case import NIOTestCaseNoModules


class TestWebInterface(NIOTestCaseNoModules):

    def test_web_interface(self):
        """ Asserts web interface bare functionality """
        with self.assertRaises(NotImplementedError):
            WebEngine.configure({})

        with self.assertRaises(NotImplementedError):
            WebEngine.get(80, "localhost")

        with self.assertRaises(NotImplementedError):
            WebEngine.remove_server(None)

        with self.assertRaises(NotImplementedError):
            WebEngine.get_servers()

        with self.assertRaises(NotImplementedError):
            WebEngine.get_name()

        with self.assertRaises(NotImplementedError):
            WebEngine.get_version()

        with self.assertRaises(NotImplementedError):
            WebEngine.start()

        with self.assertRaises(NotImplementedError):
            WebEngine.stop()

        with self.assertRaises(NotImplementedError):
            WebEngine.block()
