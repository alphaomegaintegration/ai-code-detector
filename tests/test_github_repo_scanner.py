"""
Unit tests for branch name validation in GitHubRepoScanner.
"""
import unittest
# pylint: disable=protected-access
from github_repo_scanner import GitHubRepoScanner

class TestBranchValidation(unittest.TestCase):
    """Test suite for branch validation logic."""

    def setUp(self):
        self.scanner = GitHubRepoScanner(verbose=False)

    def test_valid_branch_names(self):
        """Test that valid branch names are accepted."""
        valid_branches = [
            "main",
            "master",
            "feature/branch",
            "fix-bug",
            "v1.0.0",
            "user/repo/branch",
            "MyBranch.1.2"
        ]
        for branch in valid_branches:
            self.assertTrue(
                self.scanner._validate_branch_name(branch),
                f"Should accept valid branch: {branch}"
            )

    def test_invalid_branch_names(self):
        """Test that invalid branch names are rejected."""
        invalid_branches = [
            "-u",
            "--upload-pack=touch /tmp/pwned",
            "-oProxyCommand=calc",
            "branch; rm -rf /",
            "branch| echo pwned",
            "../evildir",
            "space in branch",
            "branch$name",
            "branch\\name"
        ]
        for branch in invalid_branches:
            self.assertFalse(
                self.scanner._validate_branch_name(branch),
                f"Should reject invalid branch: {branch}"
            )

    def test_scan_repository_validation(self):
        """Test that scan_repository raises ValueError for invalid branches."""
        # Test that scan_repository actually raises ValueError
        # We don't need to actually clone, just check validation
        # The URL must be valid to reach the branch validation check
        with self.assertRaises(ValueError) as cm:
            self.scanner.scan_repository(
                "https://github.com/user/repo",
                branch="-invalid"
            )
        self.assertIn("Invalid branch name", str(cm.exception))

if __name__ == '__main__':
    unittest.main()
