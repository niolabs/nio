from nio.block.base import Block
from nio.command import command
from nio.command.base import InvalidCommandArg
from nio.command.params.int import IntParameter
from nio.command.params.float import FloatParameter
from nio.command.params.string import StringParameter
from nio.util.support.block_test_case import NIOBlockTestCase


@command('dance',
         StringParameter("song", default='quuuux'),
         IntParameter("times"),
         FloatParameter("temp"))
@command('walk')
@command('sing', StringParameter("song"))
@command('quack', StringParameter("type"))
@command('eat')
@command('eat2')
class CommandBlock(Block):

    def __init__(self):
        super().__init__()
        self.song = None
        self.times = None
        self.steps = None
        self.quack_args = None
        self.quack_type = None
        self.sing_arg = None
        self.eat_args = None

    def dance(self, *args, **kwargs):
        self.song = args[0]
        self.times = args[1]

    def walk(self, *args, **kwargs):
        self.steps = kwargs['steps']

    def quack(self, *args, **kwargs):
        self.quack_type = args[0]
        self.quack_args = kwargs

    def sing(self, *args):
        self.sing_arg = args[0]

    def eat(self, **kwargs):
        self.eat_args = kwargs

    def eat2(self, meat='ham', drink='wine'):
        self.eat_args = {'meat': meat, 'drink': drink}


class TestCommand(NIOBlockTestCase):

    def setUp(self):
        super().setUp()
        self.blk = CommandBlock()
        self.configure_block(self.blk, {})
        self.blk.start()

    def test_calling_args(self):
        """Tests args are received."""
        self.blk.invoke('dance',
                        {'song': 'new Song', 'times': 3, 'temp': 23.3})
        self.assertEquals(self.blk.song, 'new Song')
        self.assertEquals(self.blk.times, 3)

    def test_calling_kwargs(self):
        """Tests kwargs are received."""
        self.blk.invoke('walk', {'steps': 3})
        self.assertEquals(self.blk.steps, 3)

    def test_all_args(self):
        """Tests args and kwargs are received."""
        self.blk.invoke('quack', {'animal': 'duck',
                                  'type': "mallard",
                                  'migrates': "no"})
        self.assertEquals(self.blk.quack_args, {'animal': 'duck',
                                                'migrates': "no"})
        self.assertEquals(self.blk.quack_type, "mallard")

    def test_fail_args(self):
        """Tests call failed when passing kwargs and they are not expected."""
        with self.assertRaises(InvalidCommandArg):
            self.blk.invoke('sing', {'song': 'Macarena', 'type': "dance"})

    def test_args_nokwargs(self):
        """Tests call is executed when args are present but kwargs are not."""
        self.blk.invoke('sing', {'song': 'Macarena'})
        self.assertEquals(self.blk.sing_arg, "Macarena")

    def test_args_all_kwargs(self):
        """Tests call is executed when only kwargs are present."""
        self.blk.eat_args = None
        expected = {'meat': 'chicken', 'drink': 'water'}
        self.blk.invoke('eat', expected)
        self.assertDictEqual(expected, self.blk.eat_args)

    def test_args_all_kwargs2(self):
        """Tests call is executed when only kwargs are present."""
        self.blk.eat_args = None
        expected = {'meat': 'chicken', 'drink': 'water'}
        self.blk.invoke('eat2', expected)
        self.assertDictEqual(expected, self.blk.eat_args)

    def test_args_all_kwargs3(self):
        """Test call is executed when kwargs are present and no param."""
        self.blk.eat_args = None
        self.blk.invoke('eat2', {})
        self.assertDictEqual({'meat': 'ham', 'drink': 'wine'},
                             self.blk.eat_args)
