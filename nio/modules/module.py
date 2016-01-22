from sys import maxsize


class Module(object):

    def __init__(self):
        self._my_proxies = []

    def initialize(self, context):
        self._my_proxies = context.proxies
        for proxy_interface, proxy_implementation in self._my_proxies:
            proxy_interface.proxy(proxy_implementation)

    def finalize(self):
        for proxy_interface, _ in reversed(self._my_proxies):
            proxy_interface.unproxy()

    def get_module_order(self):
        return maxsize
