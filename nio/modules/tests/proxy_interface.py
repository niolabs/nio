from nio.modules.proxy import ModuleProxy, proxied


class ProxyTest(ModuleProxy):

    @proxied
    def method_a(self):
        raise NotImplementedError
