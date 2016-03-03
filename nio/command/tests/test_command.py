from unittest.mock import MagicMock
from nio.block.base import Block
from nio.command.base import MissingCommandArg, InvalidCommandArg
from nio.signal.base import Signal
from nio.command import command
from nio.command.params.string import StringParameter
from nio.command.params.int import IntParameter
from nio.command.params.float import FloatParameter
from nio.command.params.dict import DictParameter
from nio.command.params.list import ListParameter
from nio.types import DictType
from nio.util.support.block_test_case import NIOBlockTestCase


@command('talk',
         StringParameter("phrase", default='quuuux'),
         IntParameter("times"), FloatParameter("ftimes"))
@command('walk', IntParameter("steps"))
@command('eat', StringParameter("food"))
@command('make_signal', DictParameter("sig"))
@command('make_multi', ListParameter(DictType, "sigs"))
@command('sing', StringParameter("song"), method="real_sing")
@command('fake_sing', StringParameter("song"), method="none_existent")
@command('lip_sing', StringParameter("song"), method="real_sing")
class CommandBlock(Block):

    # TODO: test what happens when a command defines a parameter that doesn't
    # exist on the method. (example: ftimes)
    def talk(self, phrase, times):
        for i in range(times):
            print(phrase)

    def walk(self, steps):
        print("i'm walking {} steps".format(steps))

    def eat(self, food):
        print("i'm eating {} food".format(food))

    def make_signal(self, sig):
        """ Command parameter is a dict """
        Signal(sig)

    def sing(self, song):
        print("i'm singing {} song".format(song))

    def real_sing(self, song):
        print("i'm singing {} song".format(song))


class TestCommand(NIOBlockTestCase):

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

    def test_description(self):
        """Commands have a description."""
        descr = CommandBlock.get_description()
        commands = descr.get('commands')
        self.assertIsNotNone(commands)
        self.assertIn('walk', commands)
        self.assertIn('talk', commands)
        self.assertIn('make_signal', commands)
        self.assertIsNotNone(descr.get('properties'))

    def test_invoke(self):
        """Commands can be invoked."""
        self.blk.talk = MagicMock()
        self.blk.invoke('talk', {'phrase': 'foobar', 'times': '3',
                                 'ftimes': '3.0'})
        self.blk.talk.assert_called_once_with('foobar', 3, 3.0)

    def test_invoke_dict(self):
        """Commands can be invoked with a dictionary."""
        self.blk.make_signal = MagicMock()
        self.blk.invoke('make_signal', {'sig': {'key': 'value'}})
        self.blk.make_signal.assert_called_once_with({'key': 'value'})

        # pass dict as a string, and assert that it was received as a dict
        self.blk.invoke('make_signal', {'sig': '{"key": "value"}'})
        self.blk.make_signal.assert_called_with({'key': 'value'})

        # pass an invalid string, assert that TypeError is raised
        # when converter kicks in
        with self.assertRaises(TypeError):
            self.blk.invoke('make_signal', {'sig': '{"key": value}'})

    def test_invoke_one_arg(self):
        """Methods with only one param accept something other than a dict."""
        self.blk.eat = MagicMock()
        self.blk.invoke('eat', "Bananas")
        self.blk.eat.assert_called_once_with("Bananas")

    def test_invoke_one_arg_nostring(self):
        """Methods accept string param."""
        self.blk.walk = MagicMock()
        with self.assertRaises(InvalidCommandArg):
            self.blk.invoke('walk', "The only arg")

    def test_invoke_list(self):
        """Methods can be invoked with a list."""
        self.blk.make_multi = MagicMock()
        self.blk.invoke('make_multi', {'sigs': [
            {'key1': 'val1'}, {'key2': 'val2'}
        ]})
        self.blk.make_multi.assert_called_once_with([
            {'key1': 'val1'}, {'key2': 'val2'}
        ])

    def test_bad_argument(self):
        """Raise MissingCommandArg if invoked with a missing arg."""
        with self.assertRaises(TypeError):
            self.blk.invoke('talk', {'phrase': 'foobar', 'times': 'baz',
                                     'ftimes': 'qux'})
        with self.assertRaises(MissingCommandArg):
            self.blk.invoke('walk', {'steps': None})

    def test_bogus_args(self):
        """Raise InvalidCommandArg if invoked with extra args."""
        with self.assertRaises(InvalidCommandArg):
            self.blk.invoke('talk', {
                'phrase': 'foobar',
                'times': '3',
                'ftimes': '3.0',
                'qux': '23'
            })

    def test_bogus_command(self):
        """Raise RuntimeError if a command is invoked that doesn't exist."""
        with self.assertRaises(RuntimeError):
            self.blk.invoke('fly', {'wings': 'yes plz'})

    def test_use_default(self):
        """Use default args when not invoked with an arg."""
        self.blk.talk = MagicMock()
        self.blk.invoke('talk', {'times': '3', 'ftimes': '3.0'})
        self.blk.talk.assert_called_once_with('quuuux', 3, 3.0)

    def test_bogus_param(self):
        """Command parameters must be TypedParameters."""
        with self.assertRaises(RuntimeError):

            @command('fail', int)
            class BogusBlock(Block):

                def fail(self, primitive):
                    print("this will never get called")

    def test_bogus_command_with_method(self):
        """Raise RuntimeError if a command alias doesn't exist."""
        with self.assertRaises(RuntimeError):
            self.blk.invoke('fake_sing', {'song': 'hey, baby'})

    def test_command_with_method(self):
        """Commands can be invoked through method alias."""
        self.blk.sing = MagicMock()
        self.blk.real_sing = MagicMock()
        self.blk.invoke('sing', {'song': 'my life'})
        self.blk.real_sing.assert_called_once_with("my life")
        self.assertEqual(0, self.blk.sing.call_count)

    def test_none_existent_method_command_with_method(self):
        """Command method doesn't need to exist as long as alias metho does."""
        self.blk.sing = MagicMock()
        self.blk.real_sing = MagicMock()
        # lip_sing isn't a method but's alias method is real_sing
        self.blk.invoke('lip_sing', {'song': 'my life'})
        self.blk.real_sing.assert_called_once_with("my life")
        self.assertEqual(0, self.blk.sing.call_count)
