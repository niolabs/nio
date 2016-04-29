from nio.modules.proxy import ModuleProxy
from nio.testing.test_case import NIOTestCaseNoModules


class ProxyInterface(ModuleProxy):

    incr_from_class_method = -1
    interface_class_variable = 5

    def __init__(self, my_arg=None):
        """ Follow the practice of only calling super in __init__"""
        super().__init__(my_arg)

    @classmethod
    def increment_from_class_method(cls):
        """ A classmethod that can be overridden by the implementation """
        raise NotImplementedError


class ProxyImplementation(object):

    incr_from_class_method = 1
    implementation_class_variable = 20

    def __init__(self, my_arg=None):
        pass

    @classmethod
    def increment_from_class_method(cls):
        cls.incr_from_class_method += 1
        return "IMPLEMENTATION"


class TestProxy(NIOTestCaseNoModules):

    """ Tests that assume the interface has been proxied initially """

    def setUp(self):
        super().setUp()
        # Make sure the proxy interface is unproxied already
        if ProxyInterface.proxied:
            ProxyInterface.unproxy()

    def tearDown(self):
        if ProxyInterface.proxied:
            ProxyInterface.unproxy()
        super().tearDown()

    def test_class_level_assignments(self):
        """ asserts assigning to class level variable behaviours """

        # assigning to a class level before proxying is ok
        ProxyInterface.interface_class_variable = 14
        ProxyImplementation.implementation_class_variable = 15
        ProxyInterface.proxy(ProxyImplementation)
        proxied = ProxyInterface()
        self.assertEqual(proxied.interface_class_variable, 14)
        self.assertEqual(proxied.implementation_class_variable, 15)

        ProxyImplementation.implementation_class_variable = 25
        self.assertEqual(proxied.implementation_class_variable, 25)

        # test that a new assignment directly to interface does not work
        former_value = ProxyInterface.implementation_class_variable
        ProxyInterface.implementation_class_variable = \
            ProxyInterface.implementation_class_variable + 1
        self.assertNotEqual(proxied.implementation_class_variable,
                         former_value + 1)

    def test_assign_from_method(self):

        ProxyInterface.proxy(ProxyImplementation)

        self.assertEqual(ProxyImplementation.incr_from_class_method, 1)

        ProxyInterface.increment_from_class_method()
        proxied = ProxyInterface()
        self.assertEqual(ProxyImplementation.incr_from_class_method, 2)

        # Instance gets value assigned at implementation class level
        self.assertEqual(proxied.incr_from_class_method, 2)

        # Interface does not take value assigned at implementation class level
        self.assertNotEqual(ProxyInterface.incr_from_class_method, 2)
