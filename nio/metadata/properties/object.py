from nio.metadata.properties.base import BaseProperty
from nio.metadata.properties.holder import PropertyHolder
from nio.metadata.types.object import ObjectType


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
        if not issubclass(obj_type, PropertyHolder):
            raise TypeError("Specified object type %s is not a PropertyHolder"
                            % obj_type.__class__)
        kwargs['obj_type'] = obj_type
        super().__init__(ObjectType, **kwargs)
        self.description.update(self._get_description(**kwargs))

    def _get_description(self, **kwargs):
        """ Description needs to be json serializable """
        kwargs.update(self._prepare_default(**kwargs))
        kwargs.update(self._prepare_template(**kwargs))
        kwargs['obj_type'] = str(kwargs['obj_type'])
        return kwargs

    def _prepare_template(self, **kwargs):
        # add object description
        try:
            sub_description = self.kwargs["obj_type"]().get_description()
        except:
            try:
                sub_description = self.kwargs["obj_type"].__name__
            except:
                sub_description = str(self.kwargs["obj_type"])
        return {"template": sub_description}

    def _prepare_default(self, **kwargs):
        """ default in description should be serializable """
        default = kwargs.get('default', None)
        if isinstance(default, PropertyHolder):
            default = default.to_dict()
        return {"default": default}

    def x_get_description(self):
        # add internal object description
        description.update({"template": self._type().get_description()})
        return description

    @property
    def xdefault(self):
        if isinstance(self._default, PropertyHolder):
            return self._default.get_defaults()
        else:
            return super().default
