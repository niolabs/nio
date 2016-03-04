from nio.modules.security.decorator import protected_access, _set_user
from nio.modules.security.authorizer import Authorizer, Unauthorized
from nio.testing.test_case import NIOTestCaseNoModules


class AuthorizerImpl(object):

    """ A simple authorizer implementation.

    This considers an authorization valid if the user is not a "hacker"
    """

    @classmethod
    def authorize(cls, user, task):
        if user == "hacker":
            raise Unauthorized()


class SecuredClass(object):

    def __init__(self):
        self.reset()

    @protected_access("unittest.run")
    def secured_method(self):
        self.secured_went_through = True

    def unsecured_method(self):
        self.unsecured_went_through = True

    def reset(self):
        self.secured_went_through = False
        self.unsecured_went_through = False


class TestAuthorizedAccess(NIOTestCaseNoModules):

    def setUp(self):
        super().setUp()
        Authorizer.proxy(AuthorizerImpl)

    def tearDown(self):
        Authorizer.unproxy()
        super().tearDown()

    def test_authorized_access(self):
        """ Asserts that right user is authorized to execute.
        """
        secured_class = SecuredClass()

        # A hacker should not be able to call the secured method
        _set_user("hacker")
        with self.assertRaises(Unauthorized):
            secured_class.secured_method()
        secured_class.unsecured_method()
        self.assertFalse(secured_class.secured_went_through)
        self.assertTrue(secured_class.unsecured_went_through)
        secured_class.reset()

        # Any other user should be able to though
        _set_user("guest")
        secured_class.secured_method()
        secured_class.unsecured_method()
        self.assertTrue(secured_class.secured_went_through)
        self.assertTrue(secured_class.unsecured_went_through)
        secured_class.reset()

        # The hacker should fail again, if he tries again
        _set_user("hacker")
        with self.assertRaises(Unauthorized):
            secured_class.secured_method()
        secured_class.unsecured_method()
        self.assertFalse(secured_class.secured_went_through)
        self.assertTrue(secured_class.unsecured_went_through)
