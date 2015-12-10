from copy import deepcopy


class Attribute(object):

    """Decorator for setting a class level attribute.
    A class level attribute will have attached a list of values, i.e.,
    input = ["input1", "input2", ...]
    """

    attributes_format = "{0}_attributes"

    def __init__(self, attribute, value):
        """ Used to add a value to an attribute

        Args:
            attribute: Attribute type (input, output)
            value: entry to add to attribute
        """

        self._attribute = attribute
        self._value = value

    def __call__(self, cls):
        # find out class entry
        entry = Attribute.attributes_format.format(cls.__name__)
        if not hasattr(cls, entry):
            setattr(cls, entry, {})
        attributes = getattr(cls, entry)

        # store attribute definition
        if self._attribute not in attributes:
            attributes[self._attribute] = [self._value]
        else:
            if self._value not in attributes[self._attribute]:
                attributes[self._attribute].append(self._value)

        return cls


def get_class_attribute(cls, name):
    """ Provides entries for a given attribute

    Args:
        cls: class name
        name: attribute name

    Returns:
        attributes defined with @Attribute
    """

    attribute = set()
    for _class in cls.__bases__:
        attribute |= get_class_attribute(_class, name)

    # Add entries from this class to the set of attributes
    entry = Attribute.attributes_format.format(cls.__name__)
    class_attribute = getattr(cls, entry, {})
    attribute |= set(class_attribute.get(name, []))

    return attribute


def get_class_attributes(cls):
    """ Provides attribute entries for a given class

    Args:
        cls: class name

    Returns:
        attributes defined with @Attribute
    """

    attributes = {}
    for _class in cls.__bases__:
        attributes.update(get_class_attributes(_class))

    entry = Attribute.attributes_format.format(cls.__name__)
    class_attributes = getattr(cls, entry, {})

    # perform a deepcopy so that referenced-to items within
    # original dictionary remain intact
    attributes = deepcopy(attributes)
    for key in class_attributes:
        if key in attributes:
            # if key is in, then merge with this class attributes
            for attribute in class_attributes[key]:
                if attribute not in attributes[key]:
                    attributes[key].append(attribute)
        else:
            # otherwise copy class attributes
            attributes[key] = class_attributes[key]

    return attributes
