class AllowNoneViolation(Exception):
    pass


class Property(object):

    """ Base class for metadata property definitions.

    """

    def serialize(self, instance):
        """Return the serialized value belonging to the specified instance.

        This method is intended to convert the corresponding value into a
        form that is serializable by json.dumps. By passing the instance
        containing the property, this property class can look up the value
        based on the instance and perform the serialization.

        Args:
            instance (PropertyHolder): the object containing the property
                to be serialized

        Returns:
            out: A serialized version of the value
        """
        pass  # pragma: no cover

    def deserialize(self, value):
        """Return the deserialized value of the specified serialized value.

        This method is intended to convert the specified value into a
        form that is safely settable for this type of property. It defaults
        to just returning the value, assuming that the serialized form is
        settable for the property.

        Args:
            value: a serialized object, most likely the result of a
                `serialize` call at some point.

        Returns:
            out: A deserialized version of the value
        """

        return value  # pragma: no cover

    # returns a description of the property as a dictionary
    def get_description(self):
        """ Provides the property description.

        Args:
            None

        Returns:
            Property description as a dictionary

        """
        pass  # pragma: no cover

    def get_type_name(self):
        """ Provides a type name as a "string" for given property,
        to be overridden when default is not descriptive enough
        """
        pass  # pragma: no cover
