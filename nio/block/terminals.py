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

# The ID that will be used to define the original default terminal
DEFAULT_TERMINAL = "__default_terminal_value"


class TerminalType(Enum):

    """Enum specifying the different types of terminals that are possible"""

    input = "input"
    output = "output"


class Terminal(object):

    """Decorator for declaring an input or output terminal on a block"""

    def __init__(self, terminal_type, terminal_id, default=False, label=None,
                 description=None, visible=True, order=0):
        """ Create a terminal with a given type and id

        Args:
            terminal_type (TerminalType): What type of terminal should this be
            terminal_id (str): The id of the terminal
            default (bool): Whether or not this terminal is the default
                terminal on the block
            label (str): The label to use for this terminal on a UI. Defaults
                to the terminal_id
            description (str): An optional, extended description for the
                terminal that can be used on a UI
            visible (bool): Whether or not the terminal should be visible on
                the UI. Defaults to True
            order (float): A numeric value used to determine the order this
                terminal should appear on the UI. Terminals will be ordered in
                ascending order

        Raises:
            TypeError: If terminal_type is not a valid TerminalType enum
        """

        if not isinstance(terminal_type, TerminalType):
            raise TypeError("Terminal type must be a TerminalType")
        self._type = terminal_type
        self.id = terminal_id
        self.default = default
        self.label = label if label is not None else terminal_id
        self.description = description if description is not None else ''
        self.visible = visible
        self.order = order

    def __call__(self, cls):
        """The decorator method to be called on the class object.

        This method will set the proper attribute to the class to save the
        terminal information. It should return the class passed in, according
        to the decorator spec.
        """
        # find out what entry we are saving on the class
        class_entry = self._get_terminals_entry(cls, self._type)

        # Get the attributes already on the class (or a new list, if not
        # present yet), and add our current terminal to the list.
        if not hasattr(cls, class_entry):
            setattr(cls, class_entry, list())
        attributes = getattr(cls, class_entry)
        attributes.append(self)
        return cls

    def get_description(self):
        """ Return a dictionary containing the description of this terminal """
        return {
            'type': self._type.value,
            'id': self.id,
            'label': self.label,
            'description': self.description,
            'default': self.default,
            'visible': self.visible,
            'order': self.order
        }

    @classmethod
    def get_terminals_on_class(cls, class_to_inspect, terminal_type,
                               order=True):
        """ Get a list of the unique terminals on a class of a certain type

        This method will recurse up the base classes and return all of the
        unique terminals that exist on it. Unique means that only one terminal
        will be included for each terminal_id. Duplicate IDs will be given to
        the class further down the MRO chain. This allows blocks to override
        certain properties on their parent blocks' terminals.

        Args:
            class_to_inspect (Block): A class that is a sub-class of Block that
                you want to get the terminals of
            terminal_type (TerminalType): What type of terminals to look for
            order (bool): Whether or not to sort the terminals based on the
                order attribute. If not, they will be sorted from first to
                last as the classes appear in the MRO

        Returns:
            list: A list of unique terminals on this block, sorted in order
                according to the terminal's order attribute

        Raises:
            TypeError: If terminal_type is not a valid TerminalType enum
        """
        if not isinstance(terminal_type, TerminalType):
            raise TypeError("Terminal type must be a TerminalType")

        # Start off our terminals set with our class's terminals
        class_entry = cls._get_terminals_entry(class_to_inspect, terminal_type)
        terminals = getattr(class_to_inspect, class_entry, list())

        # We also want to include the terminals of all super classes if they
        # don't already exist in ours
        for _class in class_to_inspect.__bases__:
            parent_terms = cls.get_terminals_on_class(_class, terminal_type)
            for parent_term in parent_terms:
                # If we don't already have a record of the parent terminal's
                # ID, then add the parent terminal to our output list
                if parent_term.id not in [term.id for term in terminals]:
                    terminals.append(parent_term)

        # Remove the DEFAULT_TERMINAL if it has other terminals defined
        if len(terminals) > 1:
            terminals = [t for t in terminals if t.id != DEFAULT_TERMINAL]

        if order:
            # Return the terminals sorted by their order
            return sorted(terminals, key=lambda t: t.order)
        else:
            return terminals

    @classmethod
    def get_default_terminal_on_class(cls, class_to_inspect, terminal_type):
        """ Gets the default terminal of a given type on a class

        If multiple terminals are declared as default, the one on the class
        that appears first in the MRO will be used. In other words, when
        iterating up the MRO, default terminals that are detected after a
        default terminal will be ignored.

        Args:
            class_to_inspect (Block): A class that is a sub-class of Block that
                you want to get the default terminal
            terminal_type (TerminalType): What type of terminals to look for

        Returns:
            Terminal: The default terminal on the class. None if no default
                exists

        Raises:
            TypeError: If terminal_type is not a valid TerminalType enum
        """
        if not isinstance(terminal_type, TerminalType):
            raise TypeError("Terminal type must be a TerminalType")

        # Iterate through the terminals ignoring their order attribute. We need
        # to do this so that we properly recurse up the MRO
        my_terms = cls.get_terminals_on_class(
            class_to_inspect, terminal_type, order=False)
        for terminal in my_terms:
            if terminal.default:
                return terminal
        return None

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


class input(Terminal):

    """A decorator for an input terminal on a block"""

    def __init__(self, input_id, **kwargs):
        """Create an input terminal with a given id."""
        super().__init__(TerminalType.input, input_id, **kwargs)


class output(Terminal):

    """A decorator for an output terminal on a block"""

    def __init__(self, output_id, **kwargs):
        """Create an output terminal with a given id."""
        super().__init__(TerminalType.output, output_id, **kwargs)
