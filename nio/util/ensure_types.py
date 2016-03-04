from inspect import isclass


def ensure_is(obj, types, fn, msg=None):
    """ Make sure an object is of a given type

    General method for checking an object against a
    list of types. If the object does not match one of the
    types in 'types', then 'fn' (parameterized by 'obj') is
    called. If 'fn' is an Exception class, then an instance
    of that Exception class is raised.

    Args:
        obj: The object under consideration.
        types (list): A list of types.
        fn (callable): This is called when type(obj) not in types
        msg (string): Optional message for the case when 'fn' is
            as Exception

    Returns:
        obj: Either the original object (if the types match) or
            the result of 'fn(obj)'

    """
    for t in types:
        if isinstance(obj, t):
            return obj

    if isclass(fn) and issubclass(fn, Exception):
        raise fn() if msg is None else fn(msg)
    return fn(obj)


def ensure_list(obj, fn=lambda x: [x], msg=None):
    """ Make sure an object is a list.

    Less general version for the common case.
    A custom callable may be included, but the default
    parameters are convenient for checking whether an
    object is a list, wrapping it in a list if necessary.

    Args:
        obj: The object under consideration
        fn (callable): This is called when type(obj) not in types
        msg (string): Optional message for the case when 'fn' is
            as Exception

    Returns:
        obj: Either the original object or the result of
            'fn(obj)'

    """
    return ensure_is(obj, types=[list], fn=fn, msg=msg)
