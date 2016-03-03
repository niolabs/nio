from nio.types.base import Type
from nio.properties.holder import PropertyHolder


class ObjectType(Type):

    @staticmethod
    def serialize(value, **kwargs):
        """ Convert a value to a JSON serializable value """
        if value is not None:
            if isinstance(value, dict):
                # Good to go if it's already a dict
                return value
            else:
                # but to_dict if we're serialzing the PropertyHolder
                return value.to_dict()

    @staticmethod
    def deserialize(value, **kwargs):
        """ Convert value to object """
        try:
            if isinstance(value, dict):
                # Object types supports deserializing dictionaries
                sub_instance = kwargs["obj_type"]()
                # First load the value from the dict into the property holder
                sub_instance.from_dict(value)
                # Then make sure the values are valid
                sub_instance.validate_dict(value)
                return sub_instance
            elif isinstance(value, PropertyHolder):
                # And object types also work when value is already a holder
                return value
            else:
                raise Exception
        except:
            raise TypeError("Unable to cast value to object: {}".format(value))
