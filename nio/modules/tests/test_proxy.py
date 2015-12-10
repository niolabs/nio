from nio.util.support.test_case import NIOTestCase
from nio.modules.tests.proxy_interface import ProxyTest as ToProxy


class ProxyTest(object):

    def __init__(self):
        pass

    def method_a(self):
        pass

    def own_method(self):
        pass


class TestProxy(NIOTestCase):

    def setupModules(self):
        # Not using functionality modules
        pass

    def tearDownModules(self):
        # Not using functionality modules
        pass

    def setUp(self):
        super().setUp()

    def test_unproxying(self):
        """ Asserts that when creating an instance and not proxying,
        the original instance is created
        """

        not_proxied = ToProxy()
        with self.assertRaises(NotImplementedError):
            not_proxied.method_a()
        with self.assertRaises(AttributeError):
            not_proxied.own_method()


    def test_proxying(self):
        """ Asserts that when creating an instance and not proxying,
        the original instance is created
        """

        ToProxy.initialize("tests", "test_proxy", ["nio.modules"])

        proxied = ToProxy()

        # both methods can be called, and no exceptions are raised
        proxied.method_a()
        proxied.own_method()

        ToProxy.finalize()
