

class SafeEval(object):
    """ Provides a wrapper functionality white-listing python's 'eval' allowed
    functionality
    """

    # this black list is presented to provide context, not that all these
    # ops are dangerous just that some of them don't seem useful to have
    #
    #     classmethod, compile, dict, dir, eval, exec, filter, frozenset,
    #     globals, help, input, iter, locals, memoryview, open, property,
    #     range, staticmethod, super, vars, __import__
    #

    # define white-listed builtins
    _white_listed_builtins = [
        abs, all, any, ascii, bin, bool, bytearray, bytes, callable, chr,
        complex, delattr, divmod, enumerate, float, format, getattr,
        hasattr, hash, hex, id, int, isinstance, issubclass, len, list,
        map, max, min, next, object, oct, ord, pow, print, repr, reversed,
        round, set, setattr, slice, sorted, str, sum, tuple, type, zip
    ]

    # defines default modules to allow within expressions
    _modules = ["datetime", "json", "math", "random", "re"]
    # keeps a mapping at instance level holding white-listed modules
    # and functions
    _mapping = None

    @classmethod
    def set_modules(cls, modules):
        """ Allows to override modules referenced by expressions

        Args:
            modules (list): list of modules to allow
        """
        cls._modules = modules
        # mapping needs to be rebuilt
        cls._mapping = None

    @classmethod
    def eval(cls, expression, signal):
        """ Evaluates an expression against a signal

        Args:
            expression (str): expression to evaluate
            signal (Signal): signal to draw attributes from if needed
        """
        _locals_mapping = cls._get_locals_mapping()
        # add signal so that it can be referenced
        _locals_mapping["signal"] = signal

        # evaluate
        result = eval(expression, {"__builtins__": None}, cls._mapping)

        # no need to keep signal entry
        del _locals_mapping["signal"]

        return result

    @classmethod
    def _get_locals_mapping(cls):
        """ Returns locals mapping to use for 'eval'

        Manages whether mappings are available, if not, it makes
        sure to build and save them.
        """
        if cls._mapping is None:
            cls._mapping = cls._build_locals_mapping()

        return cls._mapping

    @classmethod
    def _build_locals_mapping(cls):
        """ Builds a locals mapping to use for eval

        locals mapping are built using the modules allowed
        through 'set_modules' and using the white-listed functions
        from __builtins__
        """
        locals_mapping = {}

        # import allowed modules
        for module in cls._modules:
            locals_mapping[module] = __import__(module)

        # add white-listed builtins
        for builtin in SafeEval._white_listed_builtins:
            locals_mapping[builtin.__name__] = builtin
        return locals_mapping
