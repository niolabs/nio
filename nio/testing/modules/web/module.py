from nio.testing.modules.web.engine import WebEngine
from nio.modules.web.module import WebModule


class TestingWebModule(WebModule):

    """ A version of the web module used for unit tests.

    This will proxy a simple WebEngine used for testing. Right now, this module
    implementation does nothing. A simple web server implementation is planned.
    """

    def initialize(self, context):
        super().initialize(context)
        self.proxy_web_class(WebEngine)

    def finalize(self):
        super().finalize()
