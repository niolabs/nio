from nio.modules.web import WebEngine
from nio.modules.module import Module


class WebModule(Module):

    def proxy_web_class(self, web_class):
        WebEngine.proxy(web_class)

    def finalize(self):
        WebEngine.unproxy()
        super().finalize()

    def get_module_order(self):
        return 40
