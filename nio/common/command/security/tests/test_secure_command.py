from nio.common.command import command, Command
from nio.common.command.holder import CommandHolder
from nio.common.command.params.int import IntParameter
from nio.common.command.params.string import StringParameter
from nio.common.command.security import command_security, SecureCommand
from nio.modules.security.authorize.user import user_is
from nio.modules.security.permissions.authorizer import has_permission
from nio.modules.security.authorize.role import in_role
from nio.modules.security.condition import SecureCondition
from nio.modules.security.user import User
from nio.util.support.test_case import NIOTestCase


@command_security('walk', True,
                  has_permission('*'),
                  user_is('peter'),
                  in_role('admin'))
@command('talk', StringParameter("phrase"), IntParameter("times"))
@command('walk', IntParameter("steps"))
@command('sleep')
@command_security('f_john', True, user_is('john'))
@command_security('f_either', False, user_is('john'), user_is('ben'))
@command_security('f_admin', False, in_role('admin'))
@command_security('f_perm', False,
                  has_permission(['delete_block', 'delete_service']))
class CommandHolderSecure(CommandHolder):
    pass


def is_anonymous(user):
    return user.name == "Anonymous"


@command_security('f_debug', True, is_anonymous)
class CommandHolderSecure2(CommandHolder):
    pass


@command_security('f_debug', True, has_permission('delete_block'),
                  123)
class CommandHolderSecure3(CommandHolder):
    pass


class TestCommand(NIOTestCase):

    # Test command types
    def test_get_commands(self):
        cmd = CommandHolderSecure()
        cmds = cmd.get_commands()
        self.assertEqual(7, len(cmds))
        self.assertEqual(Command, cmds['talk'].__class__)
        self.assertEqual(Command, cmds['sleep'].__class__)
        self.assertEqual(SecureCommand, cmds['f_john'].__class__)
        self.assertEqual(SecureCommand, cmds['f_admin'].__class__)
        self.assertEqual(SecureCommand, cmds['f_perm'].__class__)
        self.assertEqual(SecureCommand, cmds['walk'].__class__)

    # Test can_invoke is available, conditions are set
    def test_check_commands(self):
        cmd = CommandHolderSecure()
        f_john = cmd.get_commands()['f_john']
        self.assertIsNotNone(f_john)
        self.assertTrue(f_john.can_invoke(User('john')))
        self.assertFalse(f_john.can_invoke(None))
        self.assertTrue(SecureCondition, f_john._condition.__class__)
        self.assertEqual(1, len(f_john._condition._conditions))
        self.assertTrue(f_john._condition._all)
        f_either = cmd.get_commands()['f_either']
        self.assertIsNotNone(f_either)
        self.assertTrue(f_either.can_invoke(User('ben')))

    # Test other conditions
    def test_evaluate_conditions(self):
        cmd = CommandHolderSecure2()
        cmd_debug = cmd.get_commands()['f_debug']
        self.assertIsNotNone(cmd_debug)
        self.assertTrue(cmd_debug.can_invoke(User('Anonymous')))

    # Test invalid conditions
    def test_invalid_conditions(self):
        cmd = CommandHolderSecure3()
        cmd_debug = cmd.get_commands()['f_debug']
        self.assertIsNotNone(cmd_debug)
        self.assertFalse(cmd_debug.can_invoke(User()))
