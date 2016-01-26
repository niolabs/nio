from nio.metadata.properties.holder import PropertyHolder
from nio.metadata.properties.var import VarProperty
from nio.util.support.test_case import NIOTestCase


class ContainerClass(PropertyHolder):
    var1 = VarProperty()
    var2 = VarProperty()
    var3 = VarProperty()
    default_int = VarProperty(default=1)
    default_str = VarProperty(default='str')


class TestVarProperties(NIOTestCase):

    def test_to_from_dict(self):
        # test that different types can be defined,
        # taking as example those allowed within
        # a nio 'receiver' definition

        container_1 = ContainerClass()
        container_1.var1 = ["one", "two", "three"]
        container_1.var2 = [{"name": "one", "input": 1},
                            {"name": "two", "input": 2}]
        container_1.var3 = \
            {0: [{"name": "state", "input": 0}, "log1"],
             1: [{"name": "state", "input": 1}],
             2: ["log2"]}

        container_2 = ContainerClass()
        # Load container 2 with the dictionary of container 1
        container_2.from_dict(container_1.to_dict())

        self.assertEqual(container_1.to_dict(), container_2.to_dict())

    def test_default(self):
        container = ContainerClass()
        self.assertIsNotNone(container.default_int)
        self.assertIsNotNone(container.default_str)
        self.assertEqual(container.default_int(), 1)
        self.assertEqual(container.default_str(), 'str')
        self.assertEqual(container.default_int.default, 1)
        self.assertEqual(container.default_str.default, 'str')

    def test_experssion(self):
        container = ContainerClass()
        container.default_int = "{{ 1 + 2 }}"
        container.default_str = "{{ 'a string' }}"
        self.assertEqual(container.default_int(), 3)
        self.assertEqual(container.default_str(), 'a string')
