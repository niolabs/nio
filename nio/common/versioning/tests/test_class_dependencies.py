from nio.block.base import Block
from nio.common.versioning.dependency import DependsOn, get_class_dependencies
from nio.util.support.test_case import NIOTestCase


@DependsOn("nio", "2.0.1")
class OlderBlock(Block):
    pass


class InheritedBlock(OlderBlock):
    pass


class NoDepBlock(Block):
    pass


class TestClassDependencies(NIOTestCase):

    def test_class_dependencies(self):
        """ Asserts that dependencies are correctly saved at the
        class level
        """
        dependencies = get_class_dependencies(OlderBlock)
        self.assertIsNotNone(dependencies)
        self.assertIn("nio", dependencies)
        self.assertEqual(dependencies["nio"][1], "2.0.1")

    def test_dependency_inheritance(self):
        """ Asserts that dependencies are inherited
        """
        dependencies = get_class_dependencies(InheritedBlock)
        self.assertIsNotNone(dependencies)
        self.assertIn("nio", dependencies)
        self.assertEqual(dependencies["nio"][1], "2.0.1")

    def test_no_dependency(self):
        """ Asserts blocks can have no dependencies """
        dependencies = get_class_dependencies(NoDepBlock)
        self.assertDictEqual(dependencies, {})
