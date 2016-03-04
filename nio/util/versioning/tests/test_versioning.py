from unittest.mock import patch
from nio.util.versioning.check import get_major_version
from nio.util.versioning.dependency import validate_version
from nio.util.versioning.tests import module_version, \
    block_b_module_version, block_a_module_version
from nio.testing.test_case import NIOTestCase


class TestVersioning(NIOTestCase):
    @patch('nio.util.versioning.dependency.validate_version')
    def test_version_ok(self, mock_validate):
        mock_validate.return_value = True
        from nio.util.versioning.tests.block_a import BlockA

        mock_validate.assert_called_once_with(module_version,
                                              block_a_module_version)

    @patch('nio.util.versioning.dependency.validate_version')
    def test_version_not_ok(self, mock_validate):
        mock_validate.return_value = False
        from nio.util.versioning.tests.block_b import BlockB
        mock_validate.assert_called_once_with(module_version,
                                              block_b_module_version)

    def test_none_version_comparisons(self):
        self.assertTrue(validate_version("1.1.1", None))
        self.assertTrue(validate_version(None, "1.1.1"))
        self.assertTrue(validate_version(None, None))

    def test_major_version(self):
        major_version = get_major_version("1.0.1")
        self.assertEqual(major_version, "1.0.0")

        major_version = get_major_version("21.0.1")
        self.assertEqual(major_version, "21.0.0")

        with self.assertRaises(ValueError):
            get_major_version("non_numerical.0.1")
