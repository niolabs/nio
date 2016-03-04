from unittest.mock import patch, MagicMock
from nio.modules.initializer import ModuleInitializer
from nio.modules.proxy import ProxyNotProxied, ProxyAlreadyProxied
from nio.modules.context import ModuleContext
from nio.modules.module import Module
from nio.util.support.test_case import NIOTestCaseNoModules


class TestModuleInterface(Module):

    def __init__(self):
        super().__init__()
        self._initialized_modules = None
        self._finalized_modules = None

    def initialize(self, context):
        super().initialize(context)
        # Append this module's name to the list of modules
        # We will use this for the order of modules
        self._initialized_modules = getattr(context, "init_module_order", [])
        self._finalized_modules = getattr(
            context, "finalized_module_order", [])

        self._initialized_modules.append(self.__class__.__name__)

    def finalize(self):
        self._finalized_modules.append(self.__class__.__name__)
        super().finalize()


class FirstModuleImplementation(TestModuleInterface):

    def get_module_order(self):
        return 1


class SecondModuleImplementation(TestModuleInterface):

    def get_module_order(self):
        return 2


class TestModuleInitializer(NIOTestCaseNoModules):

    def test_register_module(self):
        """ Test that we can register then initialize a module """
        initializer = ModuleInitializer()
        impl = FirstModuleImplementation()
        ctx = ModuleContext()
        with patch.object(impl, 'initialize') as init_call:
            initializer.register_module(impl, ctx)
            # Don't want an init call after registering
            self.assertEqual(init_call.call_count, 0)
            initializer.initialize()
            init_call.assert_called_once_with(ctx)
        with patch.object(impl, 'finalize') as finalize_call:
            initializer.finalize()
            finalize_call.assert_called_once_with()

    def test_register_types(self):
        """ Asserts that registration must be called with the right type """
        initializer = ModuleInitializer()
        # Can't register a class, must be instance
        with self.assertRaises(TypeError):
            initializer.register_module(TestModuleInterface, ModuleContext())

        # Have to register with a module context
        with self.assertRaises(TypeError):
            initializer.register_module(TestModuleInterface(), {})

    def test_module_order(self):
        """ Asserts modules get initialized in the correct order """
        initializer = ModuleInitializer()
        impl1 = FirstModuleImplementation()
        impl2 = SecondModuleImplementation()
        init_module_order = list()
        finalized_module_order = list()
        ctx = ModuleContext()
        ctx.init_module_order = init_module_order
        ctx.finalized_module_order = finalized_module_order
        # Even if we register them in reverse order
        initializer.register_module(impl2, ctx)
        initializer.register_module(impl1, ctx)
        initializer.initialize()
        # Make sure, despite the order of registration, the modules were
        # initialized in the correct order (low order to high order)
        self.assertListEqual(
            init_module_order,
            ['FirstModuleImplementation', 'SecondModuleImplementation'])

        # Make sure finalization happens in the reverse order
        initializer.finalize()
        self.assertListEqual(
            finalized_module_order,
            ['SecondModuleImplementation', 'FirstModuleImplementation'])

    def test_unsafe_initialize(self):
        """ Test that an unsafe module initialize raises an exception """
        initializer = ModuleInitializer()
        # Our implementation is a module that raises ProxyAlreadyProxied
        # when it is initialized
        impl = MagicMock(spec=TestModuleInterface)
        impl.initialize.side_effect = ProxyAlreadyProxied
        initializer.register_module(impl, ModuleContext())
        with self.assertRaises(ProxyAlreadyProxied):
            initializer.initialize(safe=False)
        # We should not have finalized either
        self.assertEqual(impl.finalize.call_count, 0)

    def test_safe_initialize(self):
        """ Test that a safe module initialize tries to finalize first """
        initializer = ModuleInitializer()
        # Our implementation is a module that raises ProxyAlreadyProxied
        # the first time it is called, but succeeds the second time.
        # This simulates a module proxy getting unproxied in the middle
        impl = MagicMock(spec=TestModuleInterface)
        impl.initialize.side_effect = [ProxyAlreadyProxied, None]
        initializer.register_module(impl, ModuleContext())
        # This call should not raise an exception, it should make it to the
        # second initialize call
        initializer.initialize(safe=True)
        # We should have seen a finalize call in the middle
        impl.finalize.assert_called_once_with()

    def test_unsafe_finalize(self):
        """ Test that an unsafe module finalize raises an exception """
        initializer = ModuleInitializer()
        impl = TestModuleInterface()
        initializer.register_module(impl, ModuleContext())
        initializer.initialize()
        with patch.object(impl, 'finalize', side_effect=ProxyNotProxied):
            with self.assertRaises(ProxyNotProxied):
                initializer.finalize(safe=False)

    def test_safe_finalize(self):
        """ Test that a safe module finalize ignores the exception """
        initializer = ModuleInitializer()
        impl = TestModuleInterface()
        initializer.register_module(impl, ModuleContext())
        initializer.initialize()
        with patch.object(impl, 'finalize', side_effect=ProxyNotProxied):
            # This should just work and do nothing
            initializer.finalize(safe=True)
