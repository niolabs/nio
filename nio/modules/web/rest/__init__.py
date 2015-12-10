"""

  REST decorators

"""
import inspect


class BaseRESTDecorator(object):
    """  Base class for REST decorators

    Contains wrapper methods for gathering REST handlers
    """
    rest_attrs = {}

    @classmethod
    def set_attr(cls, cls_name, attr):
        cls.rest_attrs[cls_name] = attr

    @classmethod
    def get_attr(cls, cls_name):
        return cls.rest_attrs.get(cls_name, None)

    @classmethod
    def get_all_attrs(cls):
        return cls.rest_attrs.values()


def get_class_method_name(f):
    """ Returns the "class name.method" of a method during a decorator
        initialization
    """
    try:
        name = repr(f)
        return name.split(' ')[0:2][1]
    except:
        return None


class REST(BaseRESTDecorator):
    """ REST decorator to use at class level

    @REST()
    class TheHandler(RESTHandler)
        .....

    """

    def __init__(self):
        self.rest = None

    def __call__(self, cls):
        # verify is for a class
        if inspect.isclass(cls):
            rest = self.rest_attrs
        else:
            raise TypeError()

        def wrapped_cls(*args):
            # Retrieve list of inherited classes
            names = [k.__name__ + "." for k in inspect.getmro(cls)]
            # create dictionary with rest attrs
            list = [rest[name] for class_name in names
                    for name in rest if name.startswith(class_name)]
            attrs = dict()
            for attr in list:
                attrs[attr['name']] = attr
            # assign attrs to handler cls
            setattr(cls, "rest_attrs", attrs)
            return cls(*args)

        return wrapped_cls


class BaseRESTMethod(BaseRESTDecorator):
    """ Base class for REST method decorators
    """

    def __init__(self, url_path, method):
        self._path = url_path
        self._method = method

    def __call__(self, f):
        self.name = f.__name__
        if inspect.ismethod(f) or inspect.isfunction(f):
            # get args
            args = inspect.getargspec(f)[0]
            attr = {'name': self.name, 'path': self._path, 'args': args,
                    'method': self._method}
            cls_name = get_class_method_name(f)
            if cls_name and f != cls_name:
                BaseRESTDecorator.set_attr(cls_name, attr)

        def wrapped_f(*args):
            return f(*args)

        return wrapped_f


class GET(BaseRESTMethod):
    """ Decorator for defining a GET handler


    usage:
        @REST()
        class SomeHandler(RESTHandler):

            @GET("")
            def get_access(self, request, response):
                ....

            @GET("items/{item_id}")
            def get_access(self, item_id):
                ....

    """

    def __init__(self, url_path):
        super().__init__(url_path, 'GET')


class POST(BaseRESTMethod):
    """ Decorator for defining a GET handler


    usage:
        @REST()
        class SomeHandler(RESTHandler):

            @POST("")
            def get_access(self, request, response):
                ....

            @POST("items/{item_id}")
            def get_access(self, item_id):
                ....

    """

    def __init__(self, url_path):
        super().__init__(url_path, 'POST')


class PUT(BaseRESTMethod):
    """ Decorator for defining a GET handler


    usage:
        @REST()
        class SomeHandler(RESTHandler):

            @PUT("")
            def get_access(self, request, response):
                ....

            @PUT("items/{item_id}")
            def get_access(self, item_id):
                ....

    """

    def __init__(self, url_path):
        super().__init__(url_path, 'PUT')


class DELETE(BaseRESTMethod):
    """ Decorator for defining a DELETE handler


    usage:
        @REST()
        class SomeHandler(RESTHandler):

            @DELETE("")
            def get_access(self, request, response):
                ....

            @DELETE("items/{item_id}")
            def get_access(self, item_id):
                ....

    """

    def __init__(self, url_path):
        super().__init__(url_path, 'DELETE')
