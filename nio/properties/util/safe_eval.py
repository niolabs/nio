

class SafeEval(object):
    """ Provides a wrapper functionality white-listing python's 'eval' allowed
    functionality
    """

    # this black list is presented to provide context, not that all these
    # ops are dangerous just that some of them don't seem useful to have
    #
    #     classmethod, compile, dir, eval, exec, frozenset,
    #     globals, help, input, locals, memoryview, open, property,
    #     staticmethod, super, vars, __import__
    #

    # define white-listed builtins
    _white_listed_builtins = [
        abs, all, any, ascii, bin, bool, bytearray, bytes,
        callable, chr, complex, delattr, dict, divmod,
        enumerate, filter, float, format, getattr,
        hasattr, hash, hex, id, iter, int, isinstance, issubclass,
        len, list, map, max, min, next, object, oct, ord,
        pow, print, range, repr, reversed, round,
        set, setattr, slice, sorted, str, sum, tuple, type, zip
    ]

    # defines default modules to allow within expressions
    _modules = ["datetime", "json", "math", "random", "re", "struct"]
    # keeps eval args at instance level holding white-listed modules
    # and functions

    # a globals namespace is needed to define pretty much the same
    # functionality that is allowed within the locals namespace, it
    # has been noted that depending on the expression, python's looks
    # for the name in the globals namespace rather than the local
    # namespace (expressions including 'for' constructs in them.)
    _globals_namespace = None
    _locals_namespace = None

    @classmethod
    def set_modules(cls, modules):
        """ Allows to override modules referenced by expressions

        Args:
            modules (list): list of modules to allow
        """
        cls._modules = modules
        # eval args need to be rebuilt
        cls._globals_namespace = None
        cls._locals_namespace = None

    @classmethod
    def eval(cls, expression, signal):
        """ Evaluates an expression against a signal

        Args:
            expression (str): expression to evaluate
            signal (Signal): signal to draw attributes from if needed

        Raises:
            TypeError: when accessing not-allowed functionality or there
                is a problem with the expression
            SyntaxError: when the python construct contains a syntax error
        """
        cls._ensure_eval_args()

        # add signal so that it can be referenced
        cls._globals_namespace["signal"] = signal
        cls._locals_namespace["signal"] = signal

        # evaluate
        result = eval(expression, cls._globals_namespace, cls._locals_namespace)

        # no need to keep signal entry
        del cls._globals_namespace["signal"]
        del cls._locals_namespace["signal"]

        return result

    @classmethod
    def _ensure_eval_args(cls):
        """ Ensures args to use for eval are up to date

        locals mapping are built using the modules allowed
        through 'set_modules' and using the white-listed functions
        from __builtins__
        """
        if cls._globals_namespace is None or cls._locals_namespace is None:
            cls._globals_namespace, cls._locals_namespace = \
                cls._build_eval_args()

    @classmethod
    def _build_eval_args(cls):
        """ Builds eval arguments

        globals namespace is started by 'invalidating' all __builtins__, and
        then adding allowed functionality

        Returns:
            tuple containing globals and locals namespaces
        """
        globals_namespace = {"__builtins__": None}
        locals_namespace = {}

        # import allowed modules
        for module in cls._modules:
            locals_namespace[module] = __import__(module)
            globals_namespace[module] = locals_namespace[module]

        # add white-listed builtins
        for builtin in SafeEval._white_listed_builtins:
            locals_namespace[builtin.__name__] = builtin
            globals_namespace[builtin.__name__] = builtin

        return globals_namespace, locals_namespace
