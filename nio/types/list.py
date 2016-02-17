from nio.types.base import Type


class ListType(Type):

    @staticmethod
    def serialize(value, list_obj_type, **kwargs):
        """ Convert a value to a JSON serializable value """
        from nio.properties.holder import PropertyHolder
        serialized_list = []
        for el in value:
            # Figure out what form of serialization will happen for this type
            # TODO: do we want to remove this functionality?
            if issubclass(list_obj_type, Type):
                # if the list type is actually a Type, then use that
                serialized_list.append(list_obj_type.serialize(el))
            elif issubclass(list_obj_type, PropertyHolder):
                # the items are property holders, we need their dictionaries
                if isinstance(el, PropertyHolder):
                    # TODO: why do we also have to check that the el is a
                    # TODO: PropertyHolder? The value is already serialized?
                    serialized_list.append(el.to_dict())
                else:
                    serialized_list.append(el)
            else:
                # the element of the list is not valid
                raise TypeError('Element of list property if wrong type. '
                                'Element of type "{}" should be type "{}"'
                                .format(list_obj_type, type(el)))
        # Perform the serialization method on each element and return the list
        return serialized_list

    @staticmethod
    def deserialize(value, list_obj_type, **kwargs):
        """ Convert value to list """
        from nio.properties.holder import PropertyHolder
        if not isinstance(value, list):
            raise TypeError("Unable to cast value to list: {}".format(value))
        list_to_assign = []
        for el in value:
            # for each value in the incoming container,
            # deserialize it and add it to the list
            if issubclass(list_obj_type, Type):
                # if the list type is actually a Type, then use that
                list_to_assign.append(list_obj_type.deserialize(el))
            elif issubclass(list_obj_type, PropertyHolder):
                # the items are property holders, we load from dictionaries
                if not isinstance(el, PropertyHolder):
                    list_to_assign.append(list_obj_type().from_dict(el))
                else:
                    # It's already a property holder so we're good
                    # TODO: why would deserialize be called like this?
                    list_to_assign.append(el)
            else:
                raise TypeError(
                    "Unable to cast value to list: {}".format(value))
        return list_to_assign
