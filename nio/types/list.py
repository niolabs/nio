from nio.types.base import Type


class ListType(Type):

    @staticmethod
    def serialize(value, list_obj_type, **kwargs):
        """ Convert a value to a JSON serializable value """
        serialized_list = []
        for el in value:
            if issubclass(list_obj_type, Type):
                serialized_list.append(list_obj_type.serialize(el, **kwargs))
            else:
                # the element of the list is not valid
                raise TypeError('Element of list property if wrong type. '
                                'Element of type "{}" should be type "{}"'
                                .format(list_obj_type, type(el)))
        return serialized_list

    @staticmethod
    def deserialize(value, list_obj_type, **kwargs):
        """ Convert value to list """
        if not isinstance(value, list):
            raise TypeError("Unable to cast value to list: {}".format(value))
        list_to_assign = []
        for el in value:
            if issubclass(list_obj_type, Type):
                list_to_assign.append(list_obj_type.deserialize(el, **kwargs))
            else:
                raise TypeError(
                    "Unable to cast value to list: {}".format(value))
        return list_to_assign
