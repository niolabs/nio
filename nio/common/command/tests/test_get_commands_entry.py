from unittest.mock import MagicMock
from nio.common.block.base import Block
from nio.common.command import command
from nio.common.command.params.string import StringParameter
from nio.common.command.params.int import IntParameter
from nio.util.support.block_test_case import NIOBlockTestCase


@command('talk',
         StringParameter("phrase", default='quuuux'),
         IntParameter("times"))
class CommandBlock(Block):
    def talk(self, phrase, times):
        for i in range(times):
            print(phrase)


@command('talk2',
         StringParameter("phrase", default=''),
         IntParameter("times2"))
class CommandBlock2(CommandBlock):
    def talk2(self, phrase, times):
        for i in range(times):
            print(phrase)


@command('talk3',
         StringParameter("phrase", default=''),
         IntParameter("times3"))
class CommandBlock3(CommandBlock2):
    def talk3(self, phrase, times):
        for i in range(times):
            print(phrase)


# noinspection PyProtectedMember
class TestCommandEntries(NIOBlockTestCase):
    def setupModules(self):
        # Not using functionality modules
        pass

    def tearDownModules(self):
        # Not using functionality modules
        pass

    def setUp(self):
        super().setUp()
        self.blk = CommandBlock()
        self.configure_block(self.blk, {})
        self.blk.start()
        self.blk2 = CommandBlock2()
        self.configure_block(self.blk2, {})
        self.blk2.start()

    def test_entries(self):
        """ Make sure get_description does not affect _get_commands_entry
        functionality
        """
        desc = CommandBlock.get_description()
        self.assertIsNotNone(desc)
        desc2 = CommandBlock2.get_description()
        self.assertIsNotNone(desc2)
        desc3 = CommandBlock3.get_description()
        self.assertIsNotNone(desc3)
        commands = CommandBlock.get_commands_entry()
        self.assertIsNotNone(commands)
        self.assertIn('talk', commands)
        self.assertNotIn('talk2', commands)
        self.assertNotIn('talk3', commands)

        commands2 = CommandBlock2.get_commands_entry()
        self.assertIsNotNone(commands2)
        self.assertNotIn('talk', commands2)
        self.assertIn('talk2', commands2)
        self.assertNotIn('talk3', commands2)

        commands3 = CommandBlock3.get_commands_entry()
        self.assertIsNotNone(commands3)
        self.assertNotIn('talk', commands3)
        self.assertNotIn('talk2', commands3)
        self.assertIn('talk3', commands3)

    def test_description(self):
        descr = CommandBlock.get_description()
        commands = descr.get('commands')
        self.assertIsNotNone(commands)
        self.assertIn('talk', commands)
        self.assertNotIn('talk2', commands)

        descr2 = CommandBlock2.get_description()
        commands2 = descr2.get('commands')
        self.assertIsNotNone(commands2)
        self.assertIn('talk', commands2)
        self.assertIn('talk2', commands2)

        descr3 = CommandBlock3.get_description()
        commands3 = descr3.get('commands')
        self.assertIsNotNone(commands3)
        self.assertIn('talk', commands3)
        self.assertIn('talk2', commands3)
        self.assertIn('talk3', commands3)

    def test_invokes(self):
        self.blk = CommandBlock()
        self.configure_block(self.blk, {})
        self.blk.start()

        self.blk2 = CommandBlock2()
        self.configure_block(self.blk2, {})
        self.blk2.start()

        self.blk3 = CommandBlock3()
        self.configure_block(self.blk3, {})
        self.blk3.start()

        self.blk.talk = MagicMock()
        self.blk.invoke('talk', {'phrase': 'foobar', 'times': '3'})
        self.blk.talk.assert_called_once_with('foobar', 3)

        # blk can't invoke from CommandBlock2 and CommandBlock3
        with self.assertRaises(RuntimeError):
            self.blk.invoke('talk2', {'phrase': 'foobar', 'times': '3'})
        with self.assertRaises(RuntimeError):
            self.blk.invoke('talk3', {'phrase': 'foobar', 'times': '3'})

        # yet CommandBlock2 can "talk", talk2
        self.blk2.talk = MagicMock()
        self.blk2.invoke('talk', {'phrase': 'foobar', 'times': '3'})
        self.blk2.talk.assert_called_once_with('foobar', 3)

        self.blk2.talk2 = MagicMock()
        self.blk2.invoke('talk2', {'phrase': 'foobar', 'times2': '3'})
        self.blk2.talk2.assert_called_once_with('foobar', 3)

        # CommandBlock3 can talk, talk2, talk3
        self.blk3.talk = MagicMock()
        self.blk3.invoke('talk', {'phrase': 'foobar', 'times': '3'})
        self.blk3.talk.assert_called_once_with('foobar', 3)

        self.blk3.talk2 = MagicMock()
        self.blk3.invoke('talk2', {'phrase': 'foobar', 'times2': '3'})
        self.blk3.talk2.assert_called_once_with('foobar', 3)

        self.blk3.talk3 = MagicMock()
        self.blk3.invoke('talk3', {'phrase': 'foobar', 'times3': '3'})
        self.blk3.talk.assert_called_once_with('foobar', 3)
        self.blk3.talk3.assert_called_once_with('foobar', 3)
