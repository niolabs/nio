from nio.util.class_attributes import ClassAttributes
from nio.util.support.test_case import NIOTestCase


def function():
    pass


class Sample(object):

    def __init__(self):
        self.public_attr = 1
        self._non_public_attr = 1


class TestClassAttributes(NIOTestCase):

    def test_is_attr(self):
        self.assertFalse(ClassAttributes.is_attr(self.method))
        self.assertFalse(ClassAttributes.is_attr(function))
        self.assertFalse(ClassAttributes.is_attr(type({}.pop)))

        sample_instance = Sample()
        setattr(sample_instance, "attr", 1)
        self.assertTrue(ClassAttributes.is_attr(getattr(sample_instance,
                                                        "attr")))
        self.assertTrue(ClassAttributes.is_attr(getattr(sample_instance,
                                                        "public_attr")))
        self.assertTrue(ClassAttributes.is_attr(getattr(sample_instance,
                                                        "_non_public_attr")))

    def method(self):
        pass
