from nio.modules.security.authorize.role import RoleAuthorizer
from nio.modules.security.user import User
from nio.util.support.test_case import NIOTestCase


class TestRoleAuth(NIOTestCase):

    def test_init(self):
        role_auth = RoleAuthorizer('admin')
        self.assertEqual(list, type(role_auth._roles))
        role_auth = RoleAuthorizer(None)
        self.assertEqual(list, type(role_auth._roles))

    def test_authorize_one_role(self):
        role_auth = RoleAuthorizer('admin')
        self.assertTrue(role_auth.authorize(User('John', 'admin')))
        self.assertTrue(role_auth.authorize(User('John', ['admin', 'guest'])))
        self.assertFalse(role_auth.authorize(User('John',
                                                  ['superadmin', 'guest'])))
        self.assertFalse(role_auth.authorize(User('John', '')))

    def test_authorize_no_role(self):
        role_auth = RoleAuthorizer(None)
        self.assertFalse(role_auth.authorize(User('John', 'admin')))
        self.assertFalse(role_auth.authorize(User('John', ['admin', 'guest'])))
        self.assertFalse(role_auth.authorize(User('John',
                                                  ['superadmin', 'guest'])))
        self.assertFalse(role_auth.authorize(User('John', '')))

    def test_authorize_multiple_roles(self):
        role_auth = RoleAuthorizer(['user', 'guest'])
        self.assertFalse(role_auth.authorize(User('John', 'admin')))
        self.assertTrue(role_auth.authorize(User('John', 'user')))
        self.assertTrue(role_auth.authorize(User('John', ['admin', 'guest'])))
        self.assertFalse(role_auth.authorize(User('John', ['superadmin', ''])))
        self.assertFalse(role_auth.authorize(User('John', '')))

    def test_authorize_all(self):
        role_auth = RoleAuthorizer(['user', 'guest'], True)
        self.assertFalse(role_auth.authorize(User('John', 'admin')))
        self.assertFalse(role_auth.authorize(User('John', 'user')))
        self.assertTrue(role_auth.authorize(User('John', ['user', 'guest'])))
        self.assertTrue(role_auth.authorize(
            User('John', ['user', 'guest', 'anonymous'])))
        self.assertFalse(role_auth.authorize(User('John', ['superadmin', ''])))
        self.assertFalse(role_auth.authorize(User('John', '')))

    def test_user_has_role(self):
        john = User('John', ['user'])
        self.assertTrue(john.has_role('user'))
        self.assertFalse(john.has_role('admin'))
