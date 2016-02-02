from io import UnsupportedOperation
from os import remove
from os.path import isfile, realpath, join, dirname, basename
from unittest.mock import patch

from nio.properties import FileProperty
from nio.properties import PropertyHolder
from nio.util.support.test_case import NIOTestCase


class FileContainerClass(PropertyHolder):
    file_property = FileProperty(default="default_filename")


class FileWritableContainerClass(PropertyHolder):
    file_property = FileProperty(mode="+w", default="default_filename")


class TestFileProperty(NIOTestCase):

    def setUp(self):
        file_dir_name = dirname(realpath(__file__))
        self.tmp_block_file = join(file_dir_name, 'my_file')

    def tearDown(self):
        if isfile(self.tmp_block_file):
            remove(self.tmp_block_file)

    def test_file_property(self):
        """ Asserts basic file property functionality such as value to actual
        file mapping
        """

        container = FileContainerClass()
        self.assertEqual(container.file_property.value, "default_filename")
        self.assertIsNone(container.file_property().file)

        container.file_property = __file__
        self.assertIsNotNone(container.file_property)
        self.assertTrue(isfile(container.file_property().file))

    def test_with_on_property(self):
        """ Asserts that 'with' construct works as expected
        """

        file_contents = 'file contents, to be deleted'
        with open(self.tmp_block_file, "+w") as my_stream:
            print(file_contents, file=my_stream)

        container = FileContainerClass()
        container.file_property = self.tmp_block_file

        with container.file_property() as my_stream:
            line = my_stream.read(len(file_contents))
            self.assertEqual(line, file_contents)

    def test_file_mode(self):
        """ Asserts 'mode' keyword argument when defining property
        """

        # Populate test file with some text
        file_contents = 'file contents, to be deleted'
        with open(self.tmp_block_file, "+w") as my_stream:
            print(file_contents, file=my_stream)

        container = FileContainerClass()
        container.file_property = self.tmp_block_file

        with container.file_property() as my_stream:
            with self.assertRaises(UnsupportedOperation):
                my_stream.write("not allowed")

        container = FileWritableContainerClass()
        container.file_property = self.tmp_block_file
        new_contents = "allowed"
        with container.file_property() as my_stream:
            # write from the beginning
            my_stream.seek(0)
            print(new_contents, file=my_stream)
            my_stream.flush()
            # set to read from the beginning
            my_stream.seek(0)
            file_contents = my_stream.read(len(new_contents))
            self.assertEqual(file_contents, new_contents)

    def test_absolute_file_to_environment(self):
        """ Assert that an absolute file from environment is accessed
        """
        container = FileContainerClass()
        # build absolute path to this test file
        container.file_property = __file__
        self.assertTrue(isfile(container.file_property().file))
        self.assertEqual(container.file_property().file, __file__)

    def test_relative_file_to_working_dir(self):
        """ Assert that a file from the cwd can be accessed only by name """
        container = FileContainerClass()
        # specify the tests directory and test filename only
        #  "file_property": "tests/test_file_property.py"
        container.file_property = join('tests', basename(__file__))

        # We are going to pretend that our working directory is one level up
        # from this test file's test directory
        with patch('os.getcwd', return_value=dirname(dirname(__file__))):
            self.assertIsNotNone(container.file_property().file)
            self.assertTrue(isfile(container.file_property().file))
            self.assertEqual(container.file_property().file, __file__)
