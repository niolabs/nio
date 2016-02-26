from unittest.mock import patch
from nio.command import command, Command
from nio.command.holder import CommandHolder
from nio.command.params.int import IntParameter
from nio.command.params.string import StringParameter
from nio.modules.security.authorizer import Authorizer, Unauthorized
from nio.modules.security.task import SecureTask
from nio.modules.security.user import User
from nio.util.support.test_case import NIOTestCase


@command('unsecure', tasks=[])
@command('cmd_with_params', StringParameter("phrase"), IntParameter("times"))
@command('cmd_without_params')
@command('secure_with_params', IntParameter("steps"), tasks=[SecureTask('t1')])
@command('secure_single_task', tasks=[SecureTask('valid_john')],
                  meet_all=True)
@command('secure_any_task', tasks=[SecureTask('t1'), SecureTask('t2')],
                  meet_all=False)
@command('secure_all_tasks', tasks=[SecureTask('t1'), SecureTask('t2')],
                  meet_all=True)
class CommandHolderSecure(CommandHolder):
    pass


class TestCommand(NIOTestCase):

    def get_test_modules(self):
        return super().get_test_modules() | {'security'}

    def test_get_commands(self):
        """Get commands from a command holder."""
        cmd = CommandHolderSecure()
        cmds = cmd.get_commands()
        self.assertEqual(7, len(cmds))
        self.assertIsInstance(cmds['unsecure'], Command)
        self.assertIsInstance(cmds['cmd_with_params'], Command)
        self.assertIsInstance(cmds['cmd_without_params'], Command)
        self.assertIsInstance(cmds['secure_with_params'], Command)
        self.assertIsInstance(cmds['secure_single_task'], Command)
        self.assertIsInstance(cmds['secure_any_task'], Command)
        self.assertIsInstance(cmds['secure_all_tasks'], Command)

    def test_security_tasks(self):
        """ Make sure security tasks are on the command"""
        # Default 'commands.execute' when tasks are not defined.
        cmd = CommandHolderSecure().get_commands().get('cmd_with_params')
        self.assertIsInstance(cmd, Command)
        self.assertEqual(len(cmd._tasks), 1)
        self.assertEqual(cmd._tasks[0].task, 'commands.execute')
        # Remove security
        cmd = CommandHolderSecure().get_commands().get('unsecure')
        self.assertIsInstance(cmd, Command)
        self.assertEqual(len(cmd._tasks), 0)
        # Override/add security
        cmd = CommandHolderSecure().get_commands().get('secure_any_task')
        self.assertIsInstance(cmd, Command)
        self.assertEqual(len(cmd._tasks), 2)
        self.assertEqual(cmd._tasks[0].task, 't1')
        self.assertEqual(cmd._tasks[1].task, 't2')

    def test_check_single_secure_task(self):
        """Make sure a command can be secured with a single task."""
        cmd = CommandHolderSecure().get_commands().get('secure_single_task')
        self.assertIsInstance(cmd, Command)
        # Simulate a successful authorization
        with patch.object(Authorizer, 'authorize', return_value=None):
            self.assertTrue(cmd.can_invoke(User('john')))
        # Simulate a failed authorization
        with patch.object(Authorizer, 'authorize', side_effect=Unauthorized):
            self.assertFalse(cmd.can_invoke(User('john')))

    def test_check_default_secure_task(self):
        """ Make sure a command is secured by default """
        cmd = CommandHolderSecure().get_commands().get('cmd_with_params')
        self.assertIsInstance(cmd, Command)
        # Simulate a failed authorization
        with patch.object(Authorizer, 'authorize', side_effect=Unauthorized):
            self.assertFalse(cmd.can_invoke(User('john')))

    def test_check_not_secure_task(self):
        """ Make sure a command can be made unsecure """
        cmd = CommandHolderSecure().get_commands().get('unsecure')
        self.assertIsInstance(cmd, Command)
        # Simulate a failed authorization, but comannd invoked anyway
        with patch.object(Authorizer, 'authorize', side_effect=Unauthorized):
            self.assertTrue(cmd.can_invoke(User('john')))

    def test_check_any_secure_task(self):
        """Make sure a command can be secured with any of multiple tasks."""
        cmd = CommandHolderSecure().get_commands().get('secure_any_task')
        self.assertIsInstance(cmd, Command)

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
        """Make sure a command can be secured with all of multiple tasks."""
        cmd = CommandHolderSecure().get_commands().get('secure_all_tasks')
        self.assertIsInstance(cmd, Command)

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
