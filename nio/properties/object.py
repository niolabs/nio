import inspect
from nio.properties import BaseProperty
from nio.properties import PropertyHolder
from nio.properties.util.object_type import ObjectType


class ObjectProperty(BaseProperty):
    """ Defines a property for an object type.

    Object types contain properties themselves, and must inherit from
    PropertyHolder just like the parent class.

    """

    def __init__(self, obj_type, **kwargs):
        """ Initializes the property.

        Args:
            obj_type (class): class type which is an instance of PropertyHolder
        """
        # Validate that the object is a PropertyHolder
        if not inspect.isclass(obj_type) or \
                not issubclass(obj_type, PropertyHolder):
            raise TypeError(
                "Specified object type {} is not a PropertyHolder".format(
                    obj_type.__class__))
        kwargs['obj_type'] = obj_type
        super().__init__(ObjectType, **kwargs)
        self.description.update(self._get_description(**kwargs))

    def _get_description(self, **kwargs):
        """ Description needs to be json serializable """
        kwargs.update(self._prepare_default(**kwargs))
        kwargs.update(self._prepare_template(**kwargs))
        kwargs['obj_type'] = kwargs['obj_type'].__name__
        return kwargs

    def _prepare_template(self, **kwargs):
        # add object description
        return {"template": self.kwargs["obj_type"]().get_description()}

    def _prepare_default(self, **kwargs):
        """ default in description should be serializable """
        default = kwargs.get('default', None)
        if isinstance(default, PropertyHolder):
            default = default.to_dict()
        return {"default": default}
