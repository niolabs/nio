from nio.util.versioning.check import is_version_valid, \
    compare_versions, VersionCheckResult
from nio.util.support.test_case import NIOTestCaseNoModules


class TestVersionCheck(NIOTestCaseNoModules):
    def test_valid_versions(self):
        """ Verify valid version samples
        """
        versions = ["1.2.3", "1.2.*", "1.*", "*", "1.1.1",
                    "1.0.1rc1", "1.0.b1", "21.1.1", "21.21.1",
                    "21.21.21"]
        for version in versions:
            self.assertTrue(is_version_valid(version))

    def test_invalid_versions(self):
        """ Verify invalid version samples
        """
        invalid_versions = ["1.k.3", "invalid.2.*", "not a version"]
        for invalid_version in invalid_versions:
            self.assertFalse(is_version_valid(invalid_version))

    def test_equal_comparisons(self):
        self.assertEqual(compare_versions('1.1.2', '1.1.2'),
                         VersionCheckResult.equal)
        self.assertEqual(compare_versions('1.1.2rc1', '1.1.2rc1'),
                         VersionCheckResult.equal)
        self.assertEqual(compare_versions('21.21.21', '21.21.21'),
                         VersionCheckResult.equal)
        self.assertEqual(compare_versions('1.1.2.rc1', '1.1.2-rc1'),
                         VersionCheckResult.equal)

    def test_newer_comparisons(self):
        self.assertEqual(compare_versions('2', '1.1.2'),
                         VersionCheckResult.newer)
        self.assertEqual(compare_versions('1.2.2', '1.1.2'),
                         VersionCheckResult.newer)
        self.assertEqual(compare_versions('1.2.2rc2', '1.2.2rc1'),
                         VersionCheckResult.newer)

    def test_lower_comparisons(self):
        self.assertEqual(compare_versions('1.2', '2'),
                         VersionCheckResult.older)
        self.assertEqual(compare_versions('1.2.1', '1.2.2'),
                         VersionCheckResult.older)
        self.assertEqual(compare_versions('1.2.2rc1', '1.2.2rc2'),
                         VersionCheckResult.older)
        self.assertEqual(compare_versions('1.2.2.rc1', '1.2.2-rc2'),
                         VersionCheckResult.older)
