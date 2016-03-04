from nio.properties import BaseProperty
from nio.properties import PropertyHolder
from nio.properties.util.object_type import ObjectType
from nio.types import ListType, Type


class ListProperty(BaseProperty):
    """ Defines a list property.

    List properties hold a list of object types which can contain
    properties themselves or can be nio types like IntType, etc.

    """

    def __init__(self, list_obj_type, **kwargs):
        """ Initializes the property.

        Args:
            list_obj_type (class): type of the elements to be contained
                in the list. Needs to be a subclass of nio.base.Type or
                a nio.properties.PropertyHolder
        """
        if issubclass(list_obj_type, PropertyHolder):
            kwargs['list_obj_type'] = ObjectType
            kwargs['obj_type'] = list_obj_type
        elif issubclass(list_obj_type, Type):
            kwargs['list_obj_type'] = list_obj_type
        else:
            raise TypeError("Specified list object type must be a "
                            "PropertyHolder or a nio Type")
        super().__init__(ListType, **kwargs)
        self.description.update(self._get_description(**kwargs))

    def _get_description(self, **kwargs):
        """ Description needs to be json serializable """
        kwargs.update(self._prepare_template(**kwargs))
        kwargs.update(self._prepare_default(**kwargs))
        kwargs['list_obj_type'] = kwargs['list_obj_type'].__name__
        if 'obj_type' in kwargs:
            kwargs['obj_type'] = kwargs['obj_type'].__name__
        return kwargs

    def _prepare_template(self, **kwargs):
        # add internal object description
        if "obj_type" in self.kwargs:
            # get description from PropertyHolder
            sub_description = self.kwargs["obj_type"]().get_description()
        else:
            # get class name from nio Type
            sub_description = self.kwargs["list_obj_type"].__name__
        return {"template": sub_description}

    def _prepare_default(self, **kwargs):
        """ default in description should be serializable """
        serializable_defaults = []
        defaults = kwargs.get('default', [])
        if self.is_expression(defaults) or self.is_env_var(defaults):
            # Don't mess with default if it's an expression or env var
            return {"default": defaults}
        for default in defaults:
            if isinstance(default, PropertyHolder):
                serializable_defaults.append(
                    default.get_serializable_defaults())
            else:
                serializable_defaults.append(default)
        return {"default": serializable_defaults}
