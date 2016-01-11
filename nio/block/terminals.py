"""Terminal decorators and classes for defining inputs and outputs on blocks.

A terminal is an input or an output on a block that allows the block to handle
or notify different types of signals. Often a block will want to work with
different types of data and the service may want to take a different logic path
depending on the data. Terminals are perfect for this.

A good example is the Filter block. The Filter block will have two output
terminals, one for true and one for false. Depending on the evaluation of the
filter condition, the block will notify to either the true or false output
terminal. Then, the service is free to handle those different results however
it wants.
"""

from enum import Enum


class TerminalType(Enum):

    """Enum specifying the different types of terminals that are possible"""

    input = "input"
    output = "output"


class Terminal(object):

    """Decorator for declaring an input or output terminal on a block"""

    def __init__(self, terminal_type, terminal_name):
        """ Create a terminal with a given type and name

        Args:
            terminal_type (TerminalType): What type of terminal should this be
            terminal_name (str): The name of the terminal

        Raises:
            TypeError: If terminal_type is not a valid TerminalType enum
        """

        if not isinstance(terminal_type, TerminalType):
            raise TypeError("Terminal type must be a TerminalType")
        self._type = terminal_type
        self._name = terminal_name

    def __call__(self, cls):
        """The decorator method to be called on the class object.

        This method will set the proper attribute to the class to save the
        terminal information. It should return the class passed in, according
        to the decorator spec.
        """
        # find out what entry we are saving on the class
        class_entry = self._get_terminals_entry(cls, self._type)

        # Get the attributes already on the class (or a new set, if not present
        # yet), and add our current terminal name to the set.
        if not hasattr(cls, class_entry):
            setattr(cls, class_entry, set())
        attributes = getattr(cls, class_entry)
        attributes.add(self._name)
        return cls

    @classmethod
    def get_terminals_on_class(cls, class_to_inspect, terminal_type):
        """ Get a set of the terminals on a class of a certain type

        This method will recurse up the base classes and return the union
        of all of the terminals.

        Args:
            class_to_inspect (Block): A class that is a sub-class of Block that
                you want to get the terminals of
            terminal_type (TerminalType): What type of terminals to look for

        Returns:
            set: A list of strings of the terminal names that match the type

        Raises:
            TypeError: If class_to_inspect is not a subclass of Block
            TypeError: If terminal_type is not a valid TerminalType enum
        """
        if not isinstance(terminal_type, TerminalType):
            raise TypeError("Terminal type must be a TerminalType")

        # Start off our terminals set with our class's terminals
        terminals = getattr(
            class_to_inspect,
            cls._get_terminals_entry(class_to_inspect, terminal_type),
            set())
        # We also want to include the terminals of all super classes
        for _class in class_to_inspect.__bases__:
            terminals |= cls.get_terminals_on_class(_class, terminal_type)

        return terminals

    @classmethod
    def _get_terminals_entry(cls, _class, terminal_type):
        """ Get the string for the attribute we should save to.

        This method will return a string indicating where subsequent attribute
        calls (i.e. getattr, setattr, hasattr) should be made on a class. The
        string will be unique for class names and terminal types. A different
        string needs to be returned for different classes so that it doesn't
        collide with subclasses or parent classes.

        Args:
            _class (cls): The class we will save the attribute on
            terminal_type (TerminalType): What type of terminal type we will
                be saving

        Returns:
            str: A string indicating where the attribute shoudl reside on the
                class
        """
        return "_{}_{}_attributes".format(_class.__name__, terminal_type.value)


class Input(Terminal):

    """A decorator for an input terminal on a block"""

    def __init__(self, input_name):
        """Create an input terminal with a given name."""
        super().__init__(TerminalType.input, input_name)


class Output(Terminal):

    """A decorator for an output terminal on a block"""

    def __init__(self, output_name):
        """Create an output terminal with a given name."""
        super().__init__(TerminalType.output, output_name)
