from types import BuiltinMethodType, MethodType, FunctionType


class ClassAttributes(object):

    @classmethod
    def is_attr(cls, attr):
        """ Determine from a class attribute if it is a 'data' attribute

        Args:
            attr: Attribute to check against
        """
        if (attr is BuiltinMethodType or
                isinstance(attr, BuiltinMethodType) or
                isinstance(attr, type(object().__hash__)) or
                isinstance(attr, MethodType) or
                isinstance(attr, FunctionType)):
            return False
        return True
