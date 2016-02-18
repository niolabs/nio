from nio.properties import BaseProperty
from nio.properties import PropertyHolder
from nio.properties.util.object_type import ObjectType
from nio.types import ListType


class ListProperty(BaseProperty):
    """ Defines a list property.
    List properties hold a list of object types which can contain
    properties themselves or can be simple python types like int, str, etc.

    """

    def __init__(self, list_obj_type, **kwargs):
        """ Initializes the property.

        Args:
            list_obj_type (Type): type of the elements to be contained
                in the list. Needs to be a subclass of nio.base.Type
        Keywords Args:
            obj_type (PropertyHolder): Used by ObjectType for serialize and
                deserialize.
        """
        if issubclass(list_obj_type, PropertyHolder):
            kwargs['list_obj_type'] = ObjectType
        else:
            kwargs['list_obj_type'] = list_obj_type
        kwargs['obj_type'] = list_obj_type
        super().__init__(ListType, **kwargs)
        self.description.update(self._get_description(**kwargs))

    def _get_description(self, **kwargs):
        """ Description needs to be json serializable """
        kwargs.update(self._prepare_template(**kwargs))
        kwargs.update(self._prepare_default(**kwargs))
        kwargs['list_obj_type'] = str(kwargs['list_obj_type'])
        kwargs['obj_type'] = str(kwargs['obj_type'])
        return kwargs

    def _prepare_template(self, **kwargs):
        # add internal object description
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
        serializable_defaults = []
        defaults = kwargs.get('default', [])
        if self.is_expression(defaults) or self.is_env_var(defaults):
            # Don't mess with default if it's an expression or env var
            return {"default": defaults}
        for default in defaults:
            if isinstance(default, PropertyHolder):
                serializable_defaults.append(
                    default.get_serializable_defaults())
            elif isinstance(default, BaseProperty):
                serializable_defaults.append(
                    default.description.get("default", None))
            else:
                serializable_defaults.append(default)
        return {"default": serializable_defaults}
