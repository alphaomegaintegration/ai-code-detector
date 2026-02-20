"""
Unit tests for GitHubRepoScanner including branch validation and symlink traversal checks.
"""
import unittest
import os
import shutil
import tempfile
from pathlib import Path
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
        with self.assertRaises(ValueError) as cm:
            self.scanner.scan_repository(
                "https://github.com/user/repo",
                branch="-invalid"
            )
        self.assertIn("Invalid branch name", str(cm.exception))


class TestSymlinkTraversal(unittest.TestCase):
    """Test suite for symlink traversal vulnerability."""

    def setUp(self):
        self.repo_dir = Path(tempfile.mkdtemp())
        self.scanner = GitHubRepoScanner(verbose=False)

    def tearDown(self):
        shutil.rmtree(self.repo_dir)

    def test_find_code_files_skips_symlinks_outside_repo(self):
        """Ensure symlinks pointing outside the repository are skipped."""
        # Create a secret file outside the repo
        secret_file = Path(tempfile.mkdtemp()) / "secret.txt"
        with open(secret_file, "w") as f:
            f.write("SECRET_DATA")

        try:
            # Create a symlink inside the repo pointing to the secret file
            symlink_path = self.repo_dir / "exploit.py"
            os.symlink(secret_file, symlink_path)

            # Create a legitimate file
            (self.repo_dir / "valid.py").touch()

            # Find files
            code_files = self.scanner._find_code_files(str(self.repo_dir))

            # Convert to filenames
            filenames = [f.name for f in code_files]

            # Assert valid file is found but symlink is skipped
            self.assertIn("valid.py", filenames)
            self.assertNotIn("exploit.py", filenames)

        finally:
            shutil.rmtree(secret_file.parent)

    def test_find_code_files_allows_symlinks_inside_repo(self):
        """Ensure symlinks pointing inside the repository are allowed."""
        # Create a real file inside the repo
        real_file = self.repo_dir / "real.py"
        real_file.touch()

        # Create a symlink to it
        link_file = self.repo_dir / "link.py"
        os.symlink(real_file.name, link_file)

        # Find files
        code_files = self.scanner._find_code_files(str(self.repo_dir))
        filenames = [f.name for f in code_files]

        self.assertIn("real.py", filenames)
        self.assertIn("link.py", filenames)

if __name__ == '__main__':
    unittest.main()
