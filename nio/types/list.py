from nio.types.base import Type


class ListType(Type):

    @staticmethod
    def serialize(value, **kwargs):
        """ Convert a value to a JSON serializable value """
        from nio.properties import BaseProperty
        from nio.properties.holder import PropertyHolder
        serialized_list = []
        for el in value:
            # Figure out what form of serialization will happen for this type
            # TODO: do we want to remove this functionality?
            list_obj_type = kwargs["list_obj_type"]
            if issubclass(list_obj_type, Type):
                # if the list type is actually a Type, then use that
                serialized_list.append(list_obj_type.serialize(element))
            elif issubclass(list_obj_type, BaseProperty) and \
                isinstance(el, BaseProperty):
                # the items are properties, we will call serialize
                serialized_list.append(el.serialize(el, **kwargs))
            elif issubclass(list_obj_type, PropertyHolder) and \
                isinstance(el, PropertyHolder):
                # the items are property holders, we need their dictionaries
                serialized_list.append(el.to_dict())
            else:
                # They are some other type, just use the element
                serialized_list.append(el)
        # Perform the serialization method on each element and return the list
        return serialized_list

    @staticmethod
    def deserialize(value, **kwargs):
        """ Convert value to list """
        from nio.properties import BaseProperty
        from nio.properties.holder import PropertyHolder
        if not isinstance(value, list):
            raise TypeError("Unable to cast value to list: {}".format(value))
        try:
            list_to_assign = []
            for element in value:
                # for each value in the incoming container,
                # deserialize it and add it to the list
                # Create the sub type instance
                # TODO: do we want to remove this functionality?
                list_obj_type = kwargs["list_obj_type"]
                if issubclass(list_obj_type, Type):
                    # if the list type is actually a Type, then use that
                    list_obj_inst = list_obj_type.deserialize(element)
                # Figure out what form of deserialization will happen
                elif issubclass(list_obj_type, BaseProperty) and \
                        not isinstance(element, BaseProperty):
                    # the items are properties, we will call deserialize
                    list_obj_inst = list_obj_type().deserialize(element)
                elif issubclass(list_obj_type, PropertyHolder) and \
                        not isinstance(element, PropertyHolder):
                    # the items are property holders, we load from dictionaries
                    list_obj_inst = list_obj_type().from_dict(element)
                else:
                    # They are some other type, assign val to object
                    # TODO: if the item is a BaseProperty, do we need to do
                    # something special?
                    list_obj_inst = element
                list_to_assign.append(list_obj_inst)
            return list_to_assign
        except:
            raise TypeError("Unable to cast value to list: {}".format(value))
