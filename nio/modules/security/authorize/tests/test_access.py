import threading
from unittest.mock import patch

from nio.modules.security.authorize.access import protected_access
from nio.util.support.test_case import NIOTestCase
from nio.modules.security.user import User
from nio.modules.security import Unauthorized
from nio.modules.security.permissions.authorizer \
    import PermissionAuthorizer


class SecuredClass(object):

    def __init__(self):
        self.went_through = False

    @protected_access("unittest.run")
    def secured_method(self):
        self.went_through = True


class TestAuthorizedAccess(NIOTestCase):

    def test_authorized_access(self):
        """ Asserts that right user is authorized to execute.
        """

        with patch.object(
                PermissionAuthorizer, '_get_provider_permissions',
                return_value={"tester": {"allow": ["unittest.run"]},
                              "guest": {"allow": ["unittest.view"]}}):
            secured_class = SecuredClass()

            # not even a registered user
            setattr(threading.current_thread(), "user",
                    User("hacker", ["hacker"]))
            with self.assertRaises(Unauthorized):
                secured_class.secured_method()
            self.assertFalse(secured_class.went_through)

            # a user with permissions but not the right ones
            setattr(threading.current_thread(), "user",
                    User("guest", ["guest"]))
            with self.assertRaises(Unauthorized):
                secured_class.secured_method()
            self.assertFalse(secured_class.went_through)

            # right user
            setattr(threading.current_thread(), "user",
                    User("tester", ["tester"]))
            secured_class.secured_method()
            self.assertTrue(secured_class.went_through)
