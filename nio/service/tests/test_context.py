from nio.service.context import ServiceContext
from nio.testing.test_case import NIOTestCase


class TestServiceContext(NIOTestCase):

    def test_router_settings_not_specified(self):
        # asserts that when router settings are not defined, an empty dict
        # takes its place
        context = ServiceContext({})

        self.assertTrue(isinstance(context.router_settings, dict))
        self.assertEqual(len(context.router_settings), 0)

    def test_router_settings_specified(self):
        router_settings = {"clone_signals": True}
        context = ServiceContext({}, router_settings=router_settings)

        self.assertEqual(context.router_settings, router_settings)
