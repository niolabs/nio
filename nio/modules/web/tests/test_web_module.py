from unittest.mock import patch

from nio.modules.web import WebEngine
from nio.modules.web.module import WebModule
from nio.util.support.test_case import NIOTestCaseNoModules


class TestWebModule(NIOTestCaseNoModules):

    def test_web_module(self):

        # asserts web module bare functionality
        web_module = WebModule()

        self.assertGreater(web_module.get_module_order(), 0)

        with patch('nio.modules.web.WebEngine.proxy') as patched_proxy:
            self.assertEqual(patched_proxy.call_count, 0)
            web_module.proxy_web_class(WebEngine)
            self.assertEqual(patched_proxy.call_count, 1)

        with patch('nio.modules.web.WebEngine.unproxy') as patched_unproxy:
            self.assertEqual(patched_unproxy.call_count, 0)
            web_module.finalize()
            self.assertEqual(patched_unproxy.call_count, 1)

