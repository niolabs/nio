from nio.command.holder import CommandHolder
from nio.util.support.test_case import NIOTestCaseNoModules


class SampleCommandHolder(CommandHolder):
    pass


class TestCommandHolder(NIOTestCaseNoModules):

    def test_add_invalid_command(self):
        """Make sure we can only add an actual command"""
        with self.assertRaises(TypeError):
            SampleCommandHolder.add_command("Not a command")
