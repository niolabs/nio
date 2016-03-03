from types import BuiltinMethodType, MethodType, FunctionType


class ClassAttributes(object):

    @classmethod
    def is_attr(cls, attr_value):
        """ Determine if an attribute value is a 'data' attribute.

        Args:
            attr_value: Attribute value to check against

        Returns:
            True if value is a 'data' attribute, False otherwise
        """
        if (attr_value is BuiltinMethodType or
                isinstance(attr_value, BuiltinMethodType) or
                isinstance(attr_value, type(object().__hash__)) or
                isinstance(attr_value, MethodType) or
                isinstance(attr_value, FunctionType)):
            return False
        return True
