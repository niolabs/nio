from nio.common.block.attribute.attribute import \
    Attribute, get_class_attribute as get_attribute, \
    get_class_attributes as get_attributes


def get_class_attributes(_class):
    """ Obtains input output class attributes

    For each input and output attributes 'default' gets removed when
    there is at least one definition respectively except when it is user
    defined

    Args:
        _class: class type
    """

    class_attributes = get_attributes(_class)
    # if there is more than one input, remove default when it is not
    # user defined
    if 'input' in class_attributes and \
        len(class_attributes['input']) > 1 and \
            not hasattr(_class, "user_input_default"):
        class_attributes['input'].remove('default')

    # if there is more than one output, remove default when it is not
    # user defined
    if 'output' in class_attributes and \
        len(class_attributes['output']) > 1 and \
            not hasattr(_class, "user_output_default"):
        class_attributes['output'].remove('default')
    return class_attributes


class Input(Attribute):

    def __init__(self, name):
        super().__init__("input", name)

    def __call__(self, cls):
        if cls.__name__ is not 'Block' and self._value == 'default':
            setattr(cls, "user_input_default", True)
        return super().__call__(cls)

    @classmethod
    def get_class_attribute(cls, _class):
        class_attribute = get_attribute(_class, "input")

        # if there is more than one input, remove default when it is not
        # user defined
        if len(class_attribute) > 1 and 'default' in class_attribute and \
                not hasattr(_class, "user_input_default"):
            class_attribute.remove('default')

        return class_attribute


class Output(Attribute):

    def __init__(self, name):
        super().__init__("output", name)

    def __call__(self, cls):
        if cls.__name__ is not 'Block' and self._value == 'default':
            setattr(cls, "user_output_default", True)
        return super().__call__(cls)

    @classmethod
    def get_class_attribute(cls, _class):
        class_attribute = get_attribute(_class, "output")

        # if there is more than one output, remove default when it is not
        # defined by user
        if len(class_attribute) > 1 and 'default' in class_attribute and \
                not hasattr(_class, "user_output_default"):
            class_attribute.remove('default')

        return class_attribute
