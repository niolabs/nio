from nio.metadata.types.base import Type


class ObjectType(Type):

    @staticmethod
    def serialize(value, **kwargs):
        """ Convert a value to a JSON serializable value """
        if value is not None:
            if isinstance(value, dict):
                # Good to go if it's already a dict
                # TODO: why would this ever happen?
                return value
            else:
                # but to_dict if we're serialzing the PropertyHolder
                return value.to_dict()

    @staticmethod
    def deserialize(value, **kwargs):
        """ Convert value to object """
        try:
            sub_instance = kwargs["obj_type"]()
            if isinstance(value, dict):
                # Object types supports deserializing dicationaries
                sub_instance.from_dict(value)
            else:
                # and also supports deserializing PropertyHolders
                sub_instance.from_dict(value.to_dict())
            return sub_instance
        except:
            raise TypeError("Unable to cast value to object: {}".format(value))
