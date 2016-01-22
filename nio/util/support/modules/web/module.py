from nio.util.support.modules.web import WebEngine
from nio.modules.web.module import WebModule


class TestingWebModule(WebModule):

    def initialize(self, context):
        super().initialize(context)
        self.proxy_web_class(WebEngine)

    def finalize(self):
        super().finalize()
