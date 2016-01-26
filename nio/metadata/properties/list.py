from collections import Iterable
from nio.metadata.properties.typed import TypedProperty
from nio.metadata.properties.holder import PropertyHolder
from nio.metadata.properties.old_base import Property
from nio.util import ensure_list


class ListProperty(TypedProperty):
    """ Defines a list property.
    List properties hold a list of object types which can contain
    properties themselves or can be simple python types like int, str, etc.

    """

    def __init__(self, list_obj_type, **kwargs):
        """ Initializes the property.

        Args:
            list_obj_type (object): type of the elements to be contained
                in the list. This can be a Property, PropertyHolder, or
                any other Python type

        Keyword Args:
            Property definitions

        """
        if "default" in kwargs:
            super().__init__(list, **kwargs)
        else:
            super().__init__(list, default=[], **kwargs)
        self._list_obj_type = list_obj_type

    def serialize(self, instance):
        """Retrieve the instance values and serialize each one into a list to
        be returned.
        """

        values = self.__get__(instance, self.__class__)
        out_list = []

        for el in values():
            # Figure out what form of serialization will happen for this type
            if issubclass(self._list_obj_type, Property):
                # the items are properties, we will call serialize
                out_list.append(el.serialize(self))

            elif issubclass(self._list_obj_type, PropertyHolder):
                # the items are property holders, we need their dictionaries
                out_list.append(el.to_dict())

            else:
                # They are some other type, just use the element
                out_list.append(el)

        # Perform the serialization method on each element and return the list
        return out_list

    def deserialize(self, value):
        msg = "{} cannot be serialized into a list".format(value.__class__)
        ensure_list(value, TypeError, msg)

        list_to_assign = []

        for element in value:
            # for each value in the incoming container,
            # deserialize it and add it to the list

            # Create the sub type instance
            list_obj_inst = self._list_obj_type()

            # Figure out what form of deserialization will happen
            if issubclass(self._list_obj_type, Property):
                # the items are properties, we will call deserialize
                list_obj_inst.__set__(self, list_obj_inst.deserialize(element))
            elif issubclass(self._list_obj_type, PropertyHolder):
                # the items are property holders, we load from dictionaries
                list_obj_inst.from_dict(element)
            else:
                # They are some other type, assign val to object
                list_obj_inst = element

            list_to_assign.append(list_obj_inst)

        return list_to_assign

    def get_description(self):
        description = super().get_description()
        # add internal object description
        try:
            sub_description = self._list_obj_type().get_description()
        except:
            try:
                sub_description = self._list_obj_type.__name__
            except:  # pragma: no cover
                sub_description = str(self._list_obj_type)  # pragma: no cover
        description.update({"template": sub_description})
        return description

    @property
    def default(self):
        if isinstance(self._default, list):
            defaults = []
            for value in self._default:
                if isinstance(value, PropertyHolder):
                    defaults.append(value.get_defaults())
                else:
                    defaults.append(value)
            return defaults
        else:
            return self._default

    def get_type_name(self):
        return list.__name__

    @property
    def list_obj_type(self):
        return self._list_obj_type
