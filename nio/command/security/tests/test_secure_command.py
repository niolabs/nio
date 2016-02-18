from unittest.mock import patch
from nio.command import command, Command
from nio.command.holder import CommandHolder
from nio.command.params.int import IntParameter
from nio.command.params.string import StringParameter
from nio.command.security import command_security, SecureCommand
from nio.modules.security.authorizer import Authorizer, Unauthorized
from nio.modules.security.task import SecureTask
from nio.modules.security.user import User
from nio.util.support.test_case import NIOTestCase


@command_security('to_be_renamed', SecureTask('t1'))
@command('cmd_with_params', StringParameter("phrase"), IntParameter("times"))
@command('cmd_without_params')
@command('to_be_renamed', IntParameter("steps"))
@command_security('secure_single_task', SecureTask('valid_john'),
                  meet_all=True)
@command_security('secure_any_task', SecureTask('t1'), SecureTask('t2'),
                  meet_all=False)
@command_security('secure_all_tasks', SecureTask('t1'), SecureTask('t2'),
                  meet_all=True)
class CommandHolderSecure(CommandHolder):
    pass


class TestCommand(NIOTestCase):

    def get_test_modules(self):
        return super().get_test_modules() | {'security'}

    # Test command types
    def test_get_commands(self):
        cmd = CommandHolderSecure()
        cmds = cmd.get_commands()
        self.assertEqual(6, len(cmds))
        self.assertIsInstance(cmds['cmd_with_params'], Command)
        self.assertIsInstance(cmds['cmd_without_params'], Command)
        self.assertIsInstance(cmds['to_be_renamed'], SecureCommand)
        self.assertIsInstance(cmds['secure_single_task'], SecureCommand)
        self.assertIsInstance(cmds['secure_any_task'], SecureCommand)
        self.assertIsInstance(cmds['secure_all_tasks'], SecureCommand)

    def test_check_single_secure_task(self):
        """ Make sure a command can be secured with a single task """
        cmd = CommandHolderSecure().get_commands().get('secure_single_task')
        self.assertIsInstance(cmd, SecureCommand)
        # Simulate a successful authorization
        with patch.object(Authorizer, 'authorize', return_value=None):
            self.assertTrue(cmd.can_invoke(User('john')))
        # Simulate a failed authorization
        with patch.object(Authorizer, 'authorize', side_effect=Unauthorized):
            self.assertFalse(cmd.can_invoke(User('john')))

    def test_check_any_secure_task(self):
        """ Make sure a command can be secured with any of multiple tasks """
        cmd = CommandHolderSecure().get_commands().get('secure_any_task')
        self.assertIsInstance(cmd, SecureCommand)

        # Simulate two successful authorizations
        with patch.object(Authorizer, 'authorize', return_value=None) as auth:
            self.assertTrue(cmd.can_invoke(User('john')))
            # Authorize should only be called once since we can short circuit
            # after the first success
            self.assertEqual(auth.call_count, 1)

        # Simulate one failed and one successful authorization
        with patch.object(Authorizer, 'authorize',
                          side_effect=[Unauthorized, None]) as auth:
            self.assertTrue(cmd.can_invoke(User('john')))
            # Authorize should have been called with 2 different tasks
            self.assertEqual(auth.call_count, 2)

        # Simulate two failed authorizations
        with patch.object(Authorizer, 'authorize',
                          side_effect=[Unauthorized, Unauthorized]) as auth:
            self.assertFalse(cmd.can_invoke(User('john')))
            self.assertEqual(auth.call_count, 2)

    def test_check_all_secure_task(self):
        """ Make sure a command can be secured with all of multiple tasks """
        cmd = CommandHolderSecure().get_commands().get('secure_all_tasks')
        self.assertIsInstance(cmd, SecureCommand)

        # Simulate two successful authorizations
        with patch.object(Authorizer, 'authorize', return_value=None) as auth:
            self.assertTrue(cmd.can_invoke(User('john')))
            # Authorize should have been called with 2 different tasks
            self.assertEqual(auth.call_count, 2)

        # Simulate one failed and one successful authorization
        with patch.object(Authorizer, 'authorize',
                          side_effect=[None, Unauthorized]) as auth:
            self.assertFalse(cmd.can_invoke(User('john')))
            # Authorize should have been called with 2 different tasks
            self.assertEqual(auth.call_count, 2)

        # Simulate two failed authorizations
        with patch.object(Authorizer, 'authorize',
                          side_effect=[Unauthorized, Unauthorized]) as auth:
            self.assertFalse(cmd.can_invoke(User('john')))
            # Authorize should only be called once since we can short circuit
            # after the first success
            self.assertEqual(auth.call_count, 1)

    def test_check_renamed_command(self):
        """ Make sure a renamed command can be secured """
        cmd = CommandHolderSecure().get_commands().get('to_be_renamed')
        self.assertIsInstance(cmd, SecureCommand)
        # Simulate a successful authorization
        with patch.object(Authorizer, 'authorize', return_value=None):
            self.assertTrue(cmd.can_invoke(User('john')))
        # Simulate a failed authorization
        with patch.object(Authorizer, 'authorize', side_effect=Unauthorized):
            self.assertFalse(cmd.can_invoke(User('john')))
