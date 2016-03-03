from nio.modules.web import WebHandler, StaticHandler, RESTHandler
from nio.util.support.test_case import NIOTestCaseNoModules


class TestWebHandler(NIOTestCaseNoModules):

    def test_web_handler(self):
        # asserts web handlers bare functionality

        handler = WebHandler('/')
        with self.assertRaises(NotImplementedError):
            handler.handle(None, None)

        handler = StaticHandler('/')
        with self.assertRaises(NotImplementedError):
            handler.handle(None, None)

        handler = RESTHandler('/')
        self.assertFalse(handler.is_collection())
        with self.assertRaises(NotImplementedError):
            handler.on_delete(None, None)
        with self.assertRaises(NotImplementedError):
            handler.on_get(None, None)
        with self.assertRaises(NotImplementedError):
            handler.on_options(None, None)
        with self.assertRaises(NotImplementedError):
            handler.on_post(None, None)
        with self.assertRaises(NotImplementedError):
            handler.on_put(None, None)

