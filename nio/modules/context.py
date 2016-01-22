class ModuleContext(object):

    def __init__(self, proxies=None, configuration=None):
        self.proxies = []
        if proxies is not None:
            for proxy_interface, proxy_implementation in proxies:
                self.register_proxy(proxy_interface, proxy_implementation)
        self.configuration = configuration

    def register_proxy(self, proxy_interface, proxy_implementation):
        self.proxies.append((proxy_interface, proxy_implementation))
