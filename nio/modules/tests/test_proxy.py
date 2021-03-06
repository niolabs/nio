from unittest.mock import patch
from nio.modules.proxy import ModuleProxy, ProxyNotProxied, ProxyAlreadyProxied
from nio.testing.test_case import NIOTestCaseNoModules


class ProxyInterface(ModuleProxy):

    interface_class_variable = 5

    def __init__(self, my_arg=None):
        """ Follow the practice of only calling super in __init__"""
        super().__init__(my_arg)

    def method_a(self):
        """ A public method that can be overridden by the implementation """
        raise NotImplementedError

    def _protected_proxy_method(self):
        """ A protected method that can be overridden by the implementation """
        raise NotImplementedError

    def _method_with_body(self):
        """A method that can be overridden if desired but not needed.

        If the method is not overridden, it will call the un-overrideable
        private function on the proxy interface.
        """
        return self.__private_proxy_method()

    def __private_proxy_method(self):
        """This is a "private" method denoted by two leading underscores.

        These methods are not able to be overridden by the implementation.
        """
        return "INTERFACE"

    @classmethod
    def my_overridden_classmethod(cls):
        """ A classmethod that can be overridden by the implementation """
        raise NotImplementedError

    @classmethod
    def my_non_overridden_classmethod(cls):
        """ A classmethod that will not be overridden by the implementation """
        return "INTERFACE"

    @classmethod
    def change_my_class_variable(cls, change_to, use_cls):
        """Change the class var to a value using different class references"""
        raise NotImplementedError


class ProxyImplementation(object):

    interface_class_variable = 10
    implementation_class_variable = 20

    def __init__(self, my_arg=None):
        pass

    def method_a(self):
        # Don't do anything, just don't raise the NotImplemented
        pass

    def own_method(self):
        """ A method that did not exist on the interface

        This will return my reference to my private method """
        return self.__private_proxy_method()

    def __private_proxy_method(self):
        """ Creating a private method with the same name as the one in iface

        Methods in the implementation will access this private method, but
        methods in the interface will access the interface's private method.
        """
        return "IMPLEMENTATION"

    @classmethod
    def my_overridden_classmethod(cls):
        return "IMPLEMENTATION"

    @classmethod
    def change_my_class_variable(cls, change_to, use_cls):
        """Change the class var to a value using different class references.

        If use_cls is True, the variable will be assigned using the cls
        reference. If False, it will be assigned using ProxyInterface reference
        directly.
        """
        if use_cls:
            cls.interface_class_variable = change_to
        else:
            ProxyInterface.interface_class_variable = change_to


class TestProxy(NIOTestCaseNoModules):

    """ Tests that assume the interface has been proxied initially """

    def setUp(self):
        super().setUp()
        # Make sure the proxy interface is unproxied already
        if ProxyInterface.proxied:
            ProxyInterface.unproxy()

        # Proxy the implementation on to the interface
        ProxyInterface.proxy(ProxyImplementation)
        self.assertTrue(ProxyInterface.proxied)

    def tearDown(self):
        if ProxyInterface.proxied:
            ProxyInterface.unproxy()
        super().tearDown()

    def test_isinstance(self):
        """Proxied classes and instances should subclass the interface"""
        self.assertIsInstance(ProxyInterface(), ProxyInterface)
        self.assertTrue(issubclass(ProxyInterface, ProxyInterface))

    def test_call_proxied_method(self):
        """Calling a proxied method should call the implementation's"""
        proxied = ProxyInterface()
        proxied.method_a()

    def test_call_unproxied_method(self):
        """Failing to override a method leaves it unproxied"""
        proxied = ProxyInterface()
        with self.assertRaises(NotImplementedError):
            proxied._protected_proxy_method()

    def test_interface_class_var(self):
        """We should be able to override a class variable"""
        proxied = ProxyInterface()
        self.assertEqual(proxied.interface_class_variable, 10)

    def test_implemenation_class_var(self):
        """We should be able to declare our own class variable"""
        proxied = ProxyInterface()
        self.assertEqual(proxied.implementation_class_variable, 20)

    def test_overridden_private_function(self):
        """Implmentation should be able to call its own private functions"""
        proxied = ProxyInterface()
        # own_method will call the private function on its implementation
        # we want to make sure it doesn't use the interface one
        self.assertEqual(proxied.own_method(), "IMPLEMENTATION")

    def test_non_overridden_private_function(self):
        """Interface should be able to call its own private functions"""
        proxied = ProxyInterface()
        # _method_with_body will call the private function on its class
        # we want to make sure it doesn't use the implementation one
        self.assertEqual(proxied._method_with_body(), "INTERFACE")

    def test_overridden_classmethod(self):
        """Make sure we can override a classmethod and use it on the iface"""
        self.assertEqual(
            ProxyInterface.my_overridden_classmethod(), "IMPLEMENTATION")

    def test_non_overridden_classmethod(self):
        """Make sure we can not override a classmethod and still call it"""
        self.assertEqual(
            ProxyInterface.my_non_overridden_classmethod(), "INTERFACE")


class TestNoProxy(NIOTestCaseNoModules):

    """ Tests that do not assume the interface has been proxied initially """

    def setUp(self):
        super().setUp()
        # Make sure the proxy interface is unproxied already
        if ProxyInterface.proxied:
            ProxyInterface.unproxy()

    def tearDown(self):
        if ProxyInterface.proxied:
            ProxyInterface.unproxy()
        ProxyInterface._impl_class = None
        # Reset class level variables
        ProxyInterface.interface_class_variable = 5
        ProxyImplementation.interface_class_variable = 10
        super().tearDown()

    def test_no_proxy(self):
        """No instance creation is allowed without proxying"""
        with self.assertRaises(ProxyNotProxied):
            ProxyInterface()

    def test_init_called(self):
        """Make sure the implementation's constructor is called"""
        proxy_impl_constructor_loc = "{}.{}.__init__".format(
            self.__class__.__module__, "ProxyImplementation")
        with patch(proxy_impl_constructor_loc, return_value=None) as init:
            ProxyInterface.proxy(ProxyImplementation)
            instance = ProxyInterface("test")
            init.assert_called_once_with(instance, "test")

    def test_unproxy(self):
        """Make sure unproxying cleans everything up"""
        # While we're proxied, we have the method
        ProxyInterface.proxy(ProxyImplementation)
        self.assertTrue(hasattr(ProxyInterface, 'own_method'))
        ProxyInterface.unproxy()
        # Our class variables are back to their original references
        self.assertEqual(ProxyInterface.interface_class_variable, 5)
        # After unproxying, we don't have the new methods anymore
        self.assertFalse(hasattr(ProxyInterface, 'own_method'))
        # The class method that was there originally is back
        with self.assertRaises(NotImplementedError):
            ProxyInterface.my_overridden_classmethod()

    def test_unproxy_already_unproxied(self):
        """Make sure we can't unproxy an already unproxied proxy"""
        ProxyInterface.proxy(ProxyImplementation)
        ProxyInterface.unproxy()
        with self.assertRaises(ProxyNotProxied):
            ProxyInterface.unproxy()

    def test_proxy_already_proxied(self):
        """Make sure we can't unproxy an already unproxied proxy"""
        ProxyInterface.proxy(ProxyImplementation)
        with self.assertRaises(ProxyAlreadyProxied):
            ProxyInterface.proxy(ProxyImplementation)

    def test_change_class_var_directly(self):
        """We should be able to change class variables after proxying"""
        # Start off with the variable from the interface
        self.assertEqual(ProxyInterface.interface_class_variable, 5)
        self.assertEqual(ProxyImplementation.interface_class_variable, 10)
        ProxyInterface.proxy(ProxyImplementation)
        # After proxying, the variable should come from the implementation
        proxied = ProxyInterface()
        self.assertEqual(proxied.interface_class_variable, 10)
        # Updating the implementation class variable should have no effect
        ProxyImplementation.interface_class_variable = 15
        self.assertEqual(proxied.interface_class_variable, 10)
        # We must use the interface to change the class variable after proxying
        ProxyInterface.interface_class_variable = 20
        self.assertEqual(proxied.interface_class_variable, 20)

    def test_change_class_var_with_method(self):
        """Test behavior when updating a class variable with a classmethod.

        Adjusting class variables using the cls reference of class methods
        behaves a little strangely after proxying. This test is meant to
        describe the behavior, even if it is not ideal.

        The tests make use of a classmethod that is ONLY defined on the
        implementation and not the interface. That method will change the
        class variable using either the cls reference or the ProxyInterface
        class name directly.
        """
        # Both references start off as their original defaults
        self.assertEqual(ProxyInterface.interface_class_variable, 5)
        self.assertEqual(ProxyImplementation.interface_class_variable, 10)

        # Before proxying, update the class variable
        with self.assertRaises(NotImplementedError):
            # Doesn't exist on the interface yet, hasn't been proxied
            ProxyInterface.change_my_class_variable(5, True)

        # Changing on the implementation with cls only changes the impl
        ProxyImplementation.change_my_class_variable(15, True)
        self.assertEqual(ProxyInterface.interface_class_variable, 5)
        self.assertEqual(ProxyImplementation.interface_class_variable, 15)

        # Changing on the implementation without cls only changes the interface
        ProxyImplementation.change_my_class_variable(25, False)
        self.assertEqual(ProxyInterface.interface_class_variable, 25)
        self.assertEqual(ProxyImplementation.interface_class_variable, 15)

        # Now proxy, the behavior changes after this point
        # The interface will assume the value of the implementation (15)
        ProxyInterface.proxy(ProxyImplementation)
        instantiated = ProxyInterface()

        # Changing on the interface with cls will NOT change the
        # interface or any instantiated instances of the interface.
        # This is because the cls reference comes from the implementation and
        # thus points to the implementation class
        ProxyInterface.change_my_class_variable(35, True)
        self.assertEqual(ProxyInterface.interface_class_variable, 15)
        self.assertEqual(instantiated.interface_class_variable, 15)
        self.assertEqual(ProxyImplementation.interface_class_variable, 35)

        # When using the interface to change a variable, the interface class
        # must be used directly, NOT the cls reference. Note that this does not
        # change the implementation class this time though. That tends to be ok
        # at this point though, since we should be using the interface after
        # the implementation has been proxied.
        ProxyInterface.change_my_class_variable(45, False)
        self.assertEqual(ProxyInterface.interface_class_variable, 45)
        self.assertEqual(instantiated.interface_class_variable, 45)
        self.assertEqual(ProxyImplementation.interface_class_variable, 35)

        # Calling with the implementation and cls will naturally not change the
        # interface or instantiated references
        ProxyImplementation.change_my_class_variable(55, True)
        self.assertEqual(ProxyInterface.interface_class_variable, 45)
        self.assertEqual(instantiated.interface_class_variable, 45)
        self.assertEqual(ProxyImplementation.interface_class_variable, 55)

        # If we wish to actually affect the interface and instantiated
        # references, we will need to change the variable using the
        # ProxyInterface class name directly
        ProxyImplementation.change_my_class_variable(65, False)
        self.assertEqual(ProxyInterface.interface_class_variable, 65)
        self.assertEqual(instantiated.interface_class_variable, 65)
        self.assertEqual(ProxyImplementation.interface_class_variable, 55)
