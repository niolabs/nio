from nio.modules.security.authorizer import Authorizer, Unauthorized
from nio.testing.test_case import NIOTestCaseNoModules


class AuthorizerImpl(object):

    """ A simple authorizer implementation.

    This considers an authorization valid if the task and user are the
    same thing. Definitely not recommended for production
    """

    @classmethod
    def authorize(cls, user, task):
        if user != task:
            raise Unauthorized()


class TestAuthorizer(NIOTestCaseNoModules):

    def setUp(self):
        super().setUp()
        Authorizer.proxy(AuthorizerImpl)

    def tearDown(self):
        Authorizer.unproxy()
        super().tearDown()

    def test_authorize_pass(self):
        """ Test that a valid authorize passes """
        Authorizer.authorize("test", "test")

    def test_authorize_fail(self):
        """ Test that when an authorize fails it raises Unauthorized """
        with self.assertRaises(Unauthorized):
            Authorizer.authorize("test", "fail")

    def test_authorize_multiple_all(self):
        """ Test that we can authorize multiple and have all pass """
        Authorizer.authorize_multiple(
            "test", "test", "test", "test", meet_all=True)
        with self.assertRaises(Unauthorized):
            Authorizer.authorize_multiple(
                "test", "test", "fail", "test", meet_all=True)

    def test_authorize_multiple_all_one_item(self):
        """ Test that we can authorize multiple and have 1 item pass """
        with self.assertRaises(Unauthorized):
            Authorizer.authorize_multiple("test", "fail", meet_all=True)

    def test_authorize_multiple_all_empty_list(self):
        """ Test that authorize all with an empty list passes """
        Authorizer.authorize_multiple("test", meet_all=True)

    def test_authorize_multiple_any(self):
        """ Test that we can authorize multiple and have all pass """
        Authorizer.authorize_multiple("test",
                                      "test", "test", "test", meet_all=False)
        Authorizer.authorize_multiple("test",
                                      "fail", "fail", "test", meet_all=False)
        with self.assertRaises(Unauthorized):
            Authorizer.authorize_multiple(
                "test",
                "fail",
                "fail",
                "fail",
                meet_all=False)

    def test_authorize_multiple_any_one_item(self):
        """ Test that we can authorize multiple and have 1 item pass

        This edge case is true because we expect none of our conditions to
        fail, since there are no conditions, that criteria is met.
        """
        with self.assertRaises(Unauthorized):
            Authorizer.authorize_multiple("test", "fail", meet_all=False)

    def test_authorize_multiple_any_empty_list(self):
        """ Test that authorize any with an empty list fails.

        This edge case is true because we expect at least one condition to pass
        """
        with self.assertRaises(Unauthorized):
            Authorizer.authorize_multiple("test", meet_all=False)
