import unittest
import tempfile
import shutil
import os
from pathlib import Path
from github_repo_scanner import GitHubRepoScanner

# pylint: disable=protected-access

class TestGitHubRepoScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = GitHubRepoScanner(verbose=False)

    def test_validate_branch_name(self):
        # Valid branches
        self.assertTrue(self.scanner._validate_branch_name("main"))
        self.assertTrue(self.scanner._validate_branch_name("feature/new-feature"))
        self.assertTrue(self.scanner._validate_branch_name("v1.0.0"))
        self.assertTrue(self.scanner._validate_branch_name("dev-branch_1"))

        # Invalid branches
        self.assertFalse(self.scanner._validate_branch_name("-oProxyCommand=calc"))
        self.assertFalse(self.scanner._validate_branch_name("--upload-pack=touch /tmp/pwned"))
        self.assertFalse(self.scanner._validate_branch_name("master; rm -rf /"))
        self.assertFalse(self.scanner._validate_branch_name("$(whoami)"))
        # Spaces are technically allowed in git branch names but our strict validation disallows them for security
        self.assertFalse(self.scanner._validate_branch_name("branch with spaces"))

    def test_symlink_traversal_prevention(self):
        # Setup
        base_dir = tempfile.mkdtemp()
        try:
            secret_file = Path(base_dir) / "secret.txt"
            secret_file.write_text("SECRET_DATA_DO_NOT_READ")

            repo_dir = Path(base_dir) / "repo"
            repo_dir.mkdir()

            # Create a symlink to the secret file
            symlink_file = repo_dir / "link_to_secret.py"
            os.symlink(str(secret_file), str(symlink_file))

            # Use _find_code_files
            files = self.scanner._find_code_files(str(repo_dir))

            # Check if the symlink is in the list
            found_symlink = any(f.name == "link_to_secret.py" for f in files)
            self.assertFalse(found_symlink, "Scanner should not pick up symlink to external file")

            # Also check a valid file inside repo
            valid_file = repo_dir / "valid.py"
            valid_file.write_text("print('hello')")

            files = self.scanner._find_code_files(str(repo_dir))
            found_valid = any(f.name == "valid.py" for f in files)
            self.assertTrue(found_valid, "Scanner should pick up valid file inside repo")

        finally:
            shutil.rmtree(base_dir)

if __name__ == '__main__':
    unittest.main()
